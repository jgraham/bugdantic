"""Utility functions for working with cf_user_story fields that
are used to store key: value pair data"""

from collections import defaultdict
from enum import IntEnum
from dataclasses import dataclass

import re
from typing import Iterator, Optional, Mapping, Self


def parse(
    user_story: str,
) -> Iterator[tuple[str, Optional[str], Optional[str]]]:
    """Parse the user story assuming it's lines of the form key: value.

    If there isn't a colon in the line we simply set value to the full line."""
    user_story_re = re.compile(r"^\s*([^\s]+)\s*:\s*(.*)")
    for line in user_story.splitlines():
        key = None
        value = None
        m = user_story_re.match(line)
        if m is not None:
            maybe_key, maybe_value = m.groups()
            if maybe_value:
                key = maybe_key
                value = maybe_value
        yield line, key, value


def parse_as_dict(user_story: str) -> Mapping[str, str | list[str]]:
    rv: dict[str, str | list[str]] = {}
    for _, key, value in parse(user_story):
        if key is not None and value is not None:
            if key in rv:
                current_value = rv[key]
                if isinstance(current_value, list):
                    current_value.append(value)
                else:
                    rv[key] = [current_value, value]
            else:
                rv[key] = value
    return rv


class UserStoryChangeType(IntEnum):
    APPEND = 1
    REPLACE = 2
    DELETE = 3


@dataclass(frozen=True)
class UserStoryChange:
    field: str
    type: UserStoryChangeType
    # In case of replace changes, the current value to replace or delete
    old_value: Optional[str] = None
    # In case of append or replace changes the new value to set
    new_value: Optional[str] = None

    @classmethod
    def append(cls, field: str, new_value: str) -> Self:
        return cls(field, UserStoryChangeType.APPEND, None, new_value)

    @classmethod
    def replace(cls, field: str, old_value: str, new_value: str) -> Self:
        return cls(field, UserStoryChangeType.REPLACE, old_value, new_value)

    @classmethod
    def delete(cls, field: str, old_value: str) -> Self:
        return cls(field, UserStoryChangeType.DELETE, old_value, None)


def update(user_story: str, changes: list[UserStoryChange]) -> Optional[str]:
    new_user_story = []
    user_story_updates = defaultdict(list)
    for change in changes:
        user_story_updates[change.field].append(change)

    has_updates = False
    applied_changes = set()

    for line, key, value in parse(user_story):
        if key is None or value is None:
            new_user_story.append(line)
            continue

        output_line: Optional[tuple[str, str]] = (key, value)
        if key in user_story_updates:
            changes = user_story_updates[key]
            current_value = value.strip()
            for change in changes:
                if change in applied_changes:
                    continue
                if current_value == change.old_value:
                    applied_changes.add(change)
                    if change.type == UserStoryChangeType.DELETE:
                        output_line = None
                        has_updates = True
                    elif change.type == UserStoryChangeType.REPLACE:
                        assert change.new_value is not None
                        output_line = (key, change.new_value)
                        has_updates = True
                elif (
                    change.type == UserStoryChangeType.APPEND
                    and current_value == change.new_value
                ):
                    # If we are going to append a value that's already there
                    # do nothing
                    applied_changes.add(change)
        if output_line is not None:
            new_user_story.append(f"{output_line[0]}:{output_line[1]}")

    for changes in user_story_updates.values():
        for change in changes:
            if change not in applied_changes:
                if change.type == UserStoryChangeType.DELETE:
                    # Tried to delete a key that doesn't exist, do nothing
                    pass
                elif change.type == UserStoryChangeType.REPLACE:
                    # Tried to replace a key that doesn't exist, do nothing
                    pass
                elif change.type == UserStoryChangeType.APPEND:
                    new_user_story.append(f"{change.field}:{change.new_value}")
                    has_updates = True

    if has_updates:
        return "\n".join(new_user_story) + "\n"

    return None

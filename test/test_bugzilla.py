from typing import Any

import pytest
from pydantic import BaseModel, Field

from bugdantic import Bugzilla, BugzillaConfig
from bugdantic.bugzilla import BugComment


@pytest.fixture
def bugzilla():
    config = BugzillaConfig("https://bugzilla.mozilla.org")
    return Bugzilla(config)


def test_bug_include_default(bugzilla):
    result = bugzilla.bug(975444)
    assert result.id == 975444
    result = bugzilla.bug(975444, include_fields=["_default"])
    assert result.id == 975444


def test_bug_include_all(bugzilla):
    result = bugzilla.bug(975444, include_fields=["_all"])
    assert result.id == 975444


def test_bug_history_full(bugzilla):
    result = bugzilla.bug_history(1886129)
    assert result.id == 1886129


def test_search_include_history(bugzilla):
    bugs = [423488, 1749533]
    result = bugzilla.search({"id": bugs}, include_fields=["id", "history"])
    for expected_id, bug in zip(bugs, sorted(result, key=lambda x: x.id)):
        assert bug.id == expected_id
        assert isinstance(bug.history, list)


def test_search_include_comments_and_attachments(bugzilla):
    bugs = [423488, 1749533]
    result = bugzilla.search(
        {"id": bugs}, include_fields=["id", "comments", "attachments"]
    )
    for expected_id, bug in zip(bugs, sorted(result, key=lambda x: x.id)):
        assert bug.id == expected_id
        assert isinstance(bug.comments, list)
        assert isinstance(bug.attachments, list)
        for item in bug.attachments:
            assert "data" not in item


def test_search_include_attachments_exclude_data(bugzilla):
    bugs = [423488, 1749533]
    result = bugzilla.search(
        {"id": bugs},
        include_fields=["id", "comments", "attachments"],
        exclude_fields=["attachments.data"],
    )
    for expected_id, bug in zip(bugs, sorted(result, key=lambda x: x.id)):
        assert bug.id == expected_id
        assert isinstance(bug.comments, list)
        assert isinstance(bug.attachments, list)
        for item in bug.attachments:
            assert "data" not in item


def test_bug_as(bugzilla):
    class BugData(BaseModel):
        id: int
        cf_user_story: str

    result = bugzilla.bug_as(975444, BugData)
    assert isinstance(result, BugData)
    assert result.id == 975444
    assert result.cf_user_story is not None


def test_search_as(bugzilla):
    class BugData(BaseModel):
        id: int
        comments: list[BugComment]

    bugs = [423488, 1749533]
    result = bugzilla.search_as({"id": bugs}, BugData)
    for expected_id, bug in zip(bugs, sorted(result, key=lambda x: x.id)):
        assert isinstance(bug, BugData)
        assert bug.id == expected_id
        assert isinstance(bug.comments, list)


def test_bug_as_alias(bugzilla):
    class BugData(BaseModel):
        id: int
        user_story: str = Field(alias="cf_user_story")

    result = bugzilla.bug_as(975444, BugData)
    assert isinstance(result, BugData)
    assert result.id == 975444
    assert result.user_story is not None


def test_bug_as_validation_alias(bugzilla):
    class BugData(BaseModel):
        id: int
        user_story: str = Field(
            validation_alias="cf_user_story", alias="raw_user_story"
        )

    result = bugzilla.bug_as(975444, BugData)
    assert isinstance(result, BugData)
    assert result.id == 975444
    assert result.user_story is not None


def test_bug_as_exclude(bugzilla):
    class BugData(BaseModel):
        id: int
        attachments: list[dict[str, Any]]

    result = bugzilla.bug_as(975444, BugData, exclude_fields=["attachments.data"])
    assert isinstance(result, BugData)
    assert result.id == 975444
    assert result.attachments
    assert all("data" not in item for item in result.attachments)


def test_comment(bugzilla):
    result = bugzilla.comments([18109498, 18109500])
    assert all(isinstance(item, BugComment) for item in result)
    assert len(result) == 2
    assert {item.id for item in result} == {18109498, 18109500}


def test_comment_as(bugzilla):
    class CommentReactions(BaseModel):
        id: int
        reactions: dict[str, int]

    result = bugzilla.comments_as([18109498, 18109500], CommentReactions)
    assert all(isinstance(item, CommentReactions) for item in result)
    assert {item.id for item in result} == {18109498, 18109500}
    assert all(isinstance(item.reactions, dict) for item in result)

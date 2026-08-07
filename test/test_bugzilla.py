import pytest
from pydantic import BaseModel

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

import pytest

from bugdantic import Bugzilla, BugzillaConfig


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


def test_serach_include_history(bugzilla):
    bugs = [423488, 1749533]
    result = bugzilla.search({"id": bugs}, include_fields=["id", "history"])
    for expected_id, bug in zip(bugs, sorted(result, key=lambda x: x.id)):
        assert bug.id == expected_id
        assert isinstance(bug.history, list)

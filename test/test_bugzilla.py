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

from bugdantic import userstory


def test_parse_user_story():
    user_story = """
foo:bar
abcde:
  foo : baz
some long line: with a colon
key-:value
"""
    assert list(userstory.parse(user_story)) == [
        ("", None, None),
        ("foo:bar", "foo", "bar"),
        ("abcde:", None, None),
        ("  foo : baz", "foo", "baz"),
        ("some long line: with a colon", None, None),
        ("key-:value", "key-", "value"),
    ]

    assert userstory.parse_as_dict(user_story) == {
        "foo": ["bar", "baz"],
        "key-": "value",
    }


def test_update_user_story():
    user_story = """
foo:bar
abcde:
  foo : baz
some long line: with a colon
key-:value
key:value
"""

    changes = [
        userstory.UserStoryChange.replace("foo", "bar", "foobar"),
        userstory.UserStoryChange.delete("key-", "value"),
        userstory.UserStoryChange.append("foo", "new"),
        userstory.UserStoryChange.append("new_key", "new_value"),
        # These ones shouldn't do anything
        userstory.UserStoryChange.replace("foo", "missing", "fail"),
        userstory.UserStoryChange.replace("missing", "missing", "fail"),
        userstory.UserStoryChange.delete("key", "missing"),
        userstory.UserStoryChange.delete("missing", "missing"),
    ]
    assert (
        userstory.update(user_story, changes)
        == """
foo:foobar
abcde:
foo:baz
some long line: with a colon
key:value
foo:new
new_key:new_value
"""
    )

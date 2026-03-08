from types import SimpleNamespace

from jira2md.client import _resolve_issue, _resolve_value
from jira2md.config import JiraConfig


def _make_raw_issue(
    key: str = "PROJ-1",
    summary: str = "Test",
    status_name: str = "Open",
    **custom_attrs: object,
) -> SimpleNamespace:
    """Helper to build a fake raw Jira issue."""
    fields = SimpleNamespace(
        summary=summary,
        status=SimpleNamespace(name=status_name),
    )
    for attr, val in custom_attrs.items():
        setattr(fields, attr, val)
    return SimpleNamespace(key=key, fields=fields)


# --- _resolve_value ---


def test_resolve_value_none():
    # given
    value = None

    # when
    result = _resolve_value(value)

    # then
    assert result is None


def test_resolve_value_plain_string():
    # given
    value = "hello"

    # when
    result = _resolve_value(value)

    # then
    assert result == "hello"


def test_resolve_value_plain_number():
    # given
    value = 42

    # when
    result = _resolve_value(value)

    # then
    assert result == 42


def test_resolve_value_object_with_name():
    # given
    value = SimpleNamespace(name="In Progress")

    # when
    result = _resolve_value(value)

    # then
    assert result == "In Progress"


def test_resolve_value_object_with_display_name():
    # given
    value = SimpleNamespace(displayName="Jane Doe")

    # when
    result = _resolve_value(value)

    # then
    assert result == "Jane Doe"


def test_resolve_value_list_of_objects():
    # given
    value = [
        SimpleNamespace(name="bug"),
        SimpleNamespace(name="urgent"),
    ]

    # when
    result = _resolve_value(value)

    # then
    assert result == ["bug", "urgent"]


def test_resolve_value_list_of_strings():
    # given
    value = ["label-a", "label-b"]

    # when
    result = _resolve_value(value)

    # then
    assert result == ["label-a", "label-b"]


def test_resolve_value_sprint_string_format():
    # given
    value = (
        "com.atlassian.greenhopper.service.sprint.Sprint@abc"
        "[id=1,name=Sprint 42,state=ACTIVE]"
    )

    # when
    result = _resolve_value(value)

    # then
    assert result == "Sprint 42"


def test_resolve_value_sprint_string_no_match():
    # given
    value = "com.atlassian.something[id=1,state=ACTIVE]"

    # when
    result = _resolve_value(value)

    # then — no name= present, returns original string
    assert result == value


# --- _resolve_issue ---


def test_resolve_issue_builtin_fields():
    # given
    raw = _make_raw_issue(
        key="PROJ-10",
        summary="Login broken",
        status_name="Done",
    )
    config = JiraConfig(url="", token="", fields={})

    # when
    issue = _resolve_issue(raw, config)

    # then
    assert issue.key == "PROJ-10"
    assert issue.fields["summary"] == "Login broken"
    assert issue.fields["status"] == "Done"


def test_resolve_issue_custom_field_mapping():
    # given
    raw = _make_raw_issue(customfield_10006=5.0)
    config = JiraConfig(
        url="",
        token="",
        fields={"story_points": "customfield_10006"},
    )

    # when
    issue = _resolve_issue(raw, config)

    # then
    assert issue.fields["story_points"] == 5.0


def test_resolve_issue_missing_custom_field():
    # given
    raw = _make_raw_issue()
    config = JiraConfig(
        url="",
        token="",
        fields={"sprint": "customfield_99999"},
    )

    # when
    issue = _resolve_issue(raw, config)

    # then — missing custom field resolves to None
    assert issue.fields["sprint"] is None


def test_resolve_issue_custom_field_with_name_object():
    # given
    sprint_obj = SimpleNamespace(name="Sprint 7")
    raw = _make_raw_issue(customfield_10000=sprint_obj)
    config = JiraConfig(
        url="",
        token="",
        fields={"sprint": "customfield_10000"},
    )

    # when
    issue = _resolve_issue(raw, config)

    # then
    assert issue.fields["sprint"] == "Sprint 7"


def test_resolve_issue_builtin_name_in_custom_fields_skipped():
    # given — "status" is a builtin, should not be re-resolved via custom mapping
    raw = _make_raw_issue(status_name="Open")
    config = JiraConfig(
        url="",
        token="",
        fields={"status": "customfield_99999"},
    )

    # when
    issue = _resolve_issue(raw, config)

    # then — status comes from builtin resolution, not the custom mapping
    assert issue.fields["status"] == "Open"

from unittest.mock import MagicMock

from jira2md.fields import discover_fields, print_fields

SAMPLE_FIELDS = [
    {"id": "summary", "name": "Summary", "custom": False},
    {"id": "customfield_10006", "name": "Story Points", "custom": True},
    {"id": "customfield_10000", "name": "Sprint", "custom": True},
    {"id": "customfield_10035", "name": "Acceptance Criteria", "custom": True},
    {"id": "status", "name": "Status", "custom": False},
]


def _make_jira_mock(fields: list[dict[str, object]]) -> MagicMock:
    mock = MagicMock()
    mock.fields.return_value = fields
    return mock


# --- discover_fields ---


def test_discover_fields_returns_all_sorted():
    # given
    jira = _make_jira_mock(SAMPLE_FIELDS)

    # when
    result = discover_fields(jira)

    # then
    names = [f["name"] for f in result]
    assert names == sorted(names)
    assert len(result) == 5


def test_discover_fields_filters_by_search():
    # given
    jira = _make_jira_mock(SAMPLE_FIELDS)

    # when
    result = discover_fields(jira, search="story")

    # then
    assert len(result) == 1
    assert result[0]["name"] == "Story Points"


def test_discover_fields_search_is_case_insensitive():
    # given
    jira = _make_jira_mock(SAMPLE_FIELDS)

    # when
    result = discover_fields(jira, search="SPRINT")

    # then
    assert len(result) == 1
    assert result[0]["id"] == "customfield_10000"


def test_discover_fields_search_no_match():
    # given
    jira = _make_jira_mock(SAMPLE_FIELDS)

    # when
    result = discover_fields(jira, search="nonexistent")

    # then
    assert result == []


def test_discover_fields_empty_instance():
    # given
    jira = _make_jira_mock([])

    # when
    result = discover_fields(jira)

    # then
    assert result == []


def test_discover_fields_includes_custom_flag():
    # given
    jira = _make_jira_mock(SAMPLE_FIELDS)

    # when
    result = discover_fields(jira, search="Summary")

    # then
    assert result[0]["custom"] is False


# --- print_fields ---


def test_print_fields_empty(capsys):
    # given
    fields: list[dict[str, str]] = []

    # when
    print_fields(fields)

    # then
    output = capsys.readouterr().out
    assert "No fields found." in output


def test_print_fields_formats_table(capsys):
    # given
    fields = [
        {"id": "customfield_10006", "name": "Story Points", "custom": True},
        {"id": "status", "name": "Status", "custom": False},
    ]

    # when
    print_fields(fields)

    # then
    output = capsys.readouterr().out
    assert "ID" in output
    assert "Name" in output
    assert "Custom" in output
    assert "customfield_10006" in output
    assert "Story Points" in output
    assert "yes" in output
    assert "no" in output

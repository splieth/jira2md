from jira2md.client import Issue
from jira2md.config import OutputConfig
from jira2md.renderer import render_issue


def test_render_basic_issue():
    # given
    issue = Issue(
        key="PROJ-123",
        fields={
            "key": "PROJ-123",
            "summary": "Fix login bug",
            "status": "In Progress",
            "assignee": "Jane Doe",
            "priority": "High",
        },
    )
    config = OutputConfig(
        fields=["summary", "status", "assignee", "priority"],
    )

    # when
    md = render_issue(issue, config)

    # then
    assert "# PROJ-123: Fix login bug" in md
    assert "| Status | In Progress |" in md
    assert "| Assignee | Jane Doe |" in md
    assert "| Priority | High |" in md


def test_render_with_description_section():
    # given
    issue = Issue(
        key="PROJ-456",
        fields={
            "key": "PROJ-456",
            "summary": "Add feature X",
            "status": "Open",
            "description": (
                "This is a long description\n"
                "with multiple lines\n"
                "that should be a section."
            ),
        },
    )
    config = OutputConfig(
        fields=["summary", "status", "description"],
    )

    # when
    md = render_issue(issue, config)

    # then
    assert "## Description" in md
    assert "This is a long description" in md


def test_render_with_acceptance_criteria_list():
    # given
    issue = Issue(
        key="PROJ-789",
        fields={
            "key": "PROJ-789",
            "summary": "Story with AC",
            "acceptance_criteria": [
                {"text": "User can log in", "isHeader": False},
                {"text": "Edge Cases", "isHeader": True},
                {
                    "text": "Invalid password shows error",
                    "isHeader": False,
                },
            ],
        },
    )
    config = OutputConfig(
        fields=["summary", "acceptance_criteria"],
    )

    # when
    md = render_issue(issue, config)

    # then
    assert "## Acceptance Criteria" in md
    assert "- User can log in" in md
    assert "### Edge Cases" in md
    assert "- Invalid password shows error" in md


def test_render_skips_none_fields():
    # given
    issue = Issue(
        key="PROJ-100",
        fields={
            "key": "PROJ-100",
            "summary": "Test",
            "status": "Open",
            "assignee": None,
        },
    )
    config = OutputConfig(
        fields=["summary", "status", "assignee"],
    )

    # when
    md = render_issue(issue, config)

    # then
    assert "Assignee" not in md


def test_render_list_values_in_table():
    # given
    issue = Issue(
        key="PROJ-200",
        fields={
            "key": "PROJ-200",
            "summary": "Test labels",
            "labels": ["bug", "urgent"],
        },
    )
    config = OutputConfig(fields=["summary", "labels"])

    # when
    md = render_issue(issue, config)

    # then
    assert "bug, urgent" in md

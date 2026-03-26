from dataclasses import dataclass, field
from typing import Any

from jira import JIRA

from .config import BUILTIN_FIELDS, JiraConfig


@dataclass
class Comment:
    author: str
    created: str
    body: str


@dataclass
class Issue:
    key: str
    fields: dict[str, Any] = field(default_factory=dict)
    comments: list[Comment] = field(default_factory=list)


def connect(config: JiraConfig) -> JIRA:
    """Create an authenticated Jira client."""
    return JIRA(server=config.url, token_auth=config.token)


def fetch_issue(
    jira: JIRA, key: str, config: JiraConfig, include_comments: bool = False
) -> Issue:
    """Fetch a single issue and resolve fields according to config."""
    raw = jira.issue(key)
    return _resolve_issue(raw, config, include_comments=include_comments)


def fetch_issues(
    jira: JIRA,
    jql: str,
    config: JiraConfig,
    max_results: int = 50,
    include_comments: bool = False,
) -> list[Issue]:
    """Fetch issues via JQL and resolve fields."""
    raw_issues = jira.search_issues(jql, maxResults=max_results)
    return [
        _resolve_issue(raw, config, include_comments=include_comments)
        for raw in raw_issues
    ]


def _resolve_issue(
    raw: Any, config: JiraConfig, include_comments: bool = False
) -> Issue:
    """Convert a raw Jira issue into our Issue dataclass with resolved fields."""
    resolved: dict[str, Any] = {}

    # Always include key
    resolved["key"] = raw.key

    # Resolve built-in fields
    for name in BUILTIN_FIELDS:
        if hasattr(raw.fields, name):
            resolved[name] = _resolve_value(getattr(raw.fields, name))

    # Resolve custom field mappings
    for logical_name, field_id in config.fields.items():
        if logical_name in BUILTIN_FIELDS:
            continue  # already resolved above
        raw_value = getattr(raw.fields, field_id, None)
        resolved[logical_name] = _resolve_value(raw_value)

    comments: list[Comment] = []
    if include_comments:
        raw_comments = getattr(getattr(raw.fields, "comment", None), "comments", [])
        for c in raw_comments:
            author = _resolve_value(c.author) if hasattr(c, "author") else "Unknown"
            created = getattr(c, "created", "")
            body = getattr(c, "body", "")
            comments.append(Comment(author=str(author), created=created, body=body))

    return Issue(key=raw.key, fields=resolved, comments=comments)


def _resolve_value(value: Any) -> Any:
    """Extract a displayable value from Jira's various field types."""
    if value is None:
        return None

    # Jira objects with .name (Status, Priority, IssueType, Resolution, Sprint, etc.)
    if hasattr(value, "name"):
        return value.name

    # Jira User objects
    if hasattr(value, "displayName"):
        return value.displayName

    # Lists (sprints, components, labels, fix versions, etc.)
    if isinstance(value, list):
        return [_resolve_value(item) for item in value]

    # Sprint string format: "com.atlassian.jira...Sprint@...[...,name=Sprint 1,...]"
    if (
        isinstance(value, str)
        and "name=" in value
        and value.startswith("com.atlassian")
    ):
        import re

        match = re.search(r"name=([^,\]]+)", value)
        if match:
            return match.group(1)

    return value

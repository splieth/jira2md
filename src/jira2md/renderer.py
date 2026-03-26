from pathlib import Path
from typing import Any

from .client import Issue
from .config import OutputConfig

# Fields that get their own ## section instead of a table row
SECTION_FIELDS = {"description", "acceptance_criteria"}


def render_issue(issue: Issue, config: OutputConfig) -> str:
    """Render a single issue as a Markdown string."""
    lines: list[str] = []
    summary = issue.fields.get("summary", "")
    lines.append(f"# {issue.key}: {summary}")
    lines.append("")

    # Separate fields into table fields and section fields
    table_fields = []
    section_fields = []

    for field_name in config.fields:
        if field_name in ("summary",):
            continue  # already in the heading
        value = issue.fields.get(field_name)
        if value is None:
            continue
        if _is_section_field(field_name, value):
            section_fields.append((field_name, value))
        else:
            table_fields.append((field_name, value))

    # Render metadata table
    if table_fields:
        lines.append("| Field | Value |")
        lines.append("|-------|-------|")
        for name, value in table_fields:
            display_name = _display_name(name)
            display_value = _format_value(value)
            lines.append(f"| {display_name} | {display_value} |")
        lines.append("")

    # Render section fields
    for name, value in section_fields:
        display_name = _display_name(name)
        lines.append(f"## {display_name}")
        lines.append("")
        lines.append(_format_section_value(value))
        lines.append("")

    # Render comments
    if config.include_comments and issue.comments:
        lines.append("## Comments")
        lines.append("")
        for comment in issue.comments:
            lines.append(f"### {comment.author} ({comment.created})")
            lines.append("")
            lines.append(comment.body)
            lines.append("")

    return "\n".join(lines)


def export_issue(issue: Issue, config: OutputConfig) -> Path:
    """Export a single issue to a Markdown file. Returns the file path."""
    content = render_issue(issue, config)
    filename = config.filename_pattern.format(key=issue.key) + ".md"
    output_dir = Path(config.directory)
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath = output_dir / filename
    filepath.write_text(content, encoding="utf-8")
    return filepath


def export_issues(issues: list[Issue], config: OutputConfig) -> list[Path]:
    """Export multiple issues to Markdown files."""
    return [export_issue(issue, config) for issue in issues]


def _is_section_field(name: str, value: Any) -> bool:
    """Determine if a field should be rendered as a section rather than a table row."""
    if name in SECTION_FIELDS:
        return True
    if isinstance(value, str) and (len(value) > 200 or "\n" in value):
        return True
    return bool(isinstance(value, list) and len(value) > 3)


def _display_name(name: str) -> str:
    """Convert a field name to a human-readable display name."""
    return name.replace("_", " ").title()


def _format_value(value: Any) -> str:
    """Format a value for display in a table cell."""
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def _format_section_value(value: Any) -> str:
    """Format a value for display as a section body."""
    if isinstance(value, list):
        lines = []
        for item in value:
            if isinstance(item, dict):
                text = item.get("text", item.get("name", str(item)))
                is_header = item.get("isHeader", False)
                if is_header:
                    lines.append(f"### {text}")
                else:
                    sub_lines = str(text).splitlines()
                    if sub_lines:
                        lines.append(f"- {sub_lines[0]}")
                        for sl in sub_lines[1:]:
                            lines.append(f"  {sl}")
            else:
                lines.append(f"- {item}")
        return "\n".join(lines)
    return str(value)

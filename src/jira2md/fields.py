from typing import Optional

from jira import JIRA


def discover_fields(jira: JIRA, search: Optional[str] = None) -> list[dict[str, str]]:
    """Discover available Jira fields, optionally filtered by a search term.

    Returns a list of dicts with 'id', 'name', and 'custom' keys.
    """
    all_fields = jira.fields()
    results = []
    for f in all_fields:
        name = f.get("name", "")
        field_id = f.get("id", "")
        custom = f.get("custom", False)

        if search and search.lower() not in name.lower():
            continue

        results.append(
            {
                "id": field_id,
                "name": name,
                "custom": custom,
            }
        )

    results.sort(key=lambda x: x["name"])
    return results


def print_fields(fields: list[dict[str, str]]) -> None:
    """Print discovered fields in a readable table format."""
    if not fields:
        print("No fields found.")
        return

    # Calculate column widths
    id_width = max(len(f["id"]) for f in fields)
    name_width = max(len(f["name"]) for f in fields)
    id_width = max(id_width, 2)
    name_width = max(name_width, 4)

    header = f"{'ID':<{id_width}}  {'Name':<{name_width}}  Custom"
    print(header)
    print("-" * len(header))
    for f in fields:
        custom_str = "yes" if f["custom"] else "no"
        print(f"{f['id']:<{id_width}}  {f['name']:<{name_width}}  {custom_str}")

# jira2md

> Export Jira issues to Markdown files because using Jira (or any other Atlassian product for that matter) sucks. Works as a CLI tool and as a Python library.

## Installation

```bash
uv sync
```

## Configuration

Copy `config.yaml.example` to `config.yaml` and adjust it to your Jira instance:

```yaml
jira:
  url: https://your-jira-instance.atlassian.net
  token: your-personal-access-token
  fields:
    story_points: customfield_10006
    sprint: customfield_10000
    acceptance_criteria: customfield_10035

output:
  directory: ./export
  filename_pattern: "{key}"
  fields:
    - summary
    - status
    - assignee
    - priority
    - story_points
    - sprint
    - acceptance_criteria
    - description
```

The token can also be set via the `JIRA2MD_TOKEN` environment variable instead of putting it in the file.

### Field mappings

Built-in Jira fields (summary, status, description, assignee, priority, etc.) are resolved automatically. Custom fields need to be mapped under `jira.fields` using a logical name and the Jira field ID.

The `output.fields` list controls which fields appear in the exported Markdown and in what order. Short values are rendered in a metadata table, while longer text fields like description or acceptance criteria get their own sections.

### Finding custom field IDs

If you don't know the field IDs for your Jira instance:

```bash
jira2md discover-fields
jira2md discover-fields --search "story point"
```

## CLI Usage

Export issues matching a JQL query:

```bash
jira2md export --jql "project = PROJ AND sprint in openSprints()"
```

Export a single issue:

```bash
jira2md export --key PROJ-123
```

Override the output directory:

```bash
jira2md export --jql "project = PROJ" --output-dir ./docs
```

Use a specific config file:

```bash
jira2md -c path/to/config.yaml export --jql "project = PROJ"
```

## Library Usage

```python
from jira2md import load_config, connect, fetch_issues, export_issues

config = load_config("config.yaml")
jira = connect(config.jira)
issues = fetch_issues(jira, "project = PROJ", config.jira)
paths = export_issues(issues, config.output)
```

You can also render Markdown without writing files:

```python
from jira2md import render_issue

markdown = render_issue(issue, config.output)
print(markdown)
```

## Releasing

```bash
./scripts/release.sh patch  # 0.1.0 → 0.1.1
./scripts/release.sh minor  # 0.1.0 → 0.2.0
./scripts/release.sh major  # 0.1.0 → 1.0.0
```

This bumps the version in `pyproject.toml`, commits, tags, and pushes. The push triggers a GitHub Actions workflow that publishes the package to PyPI.

## License

MIT

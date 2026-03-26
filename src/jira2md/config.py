import os
import sys
from dataclasses import dataclass, field
from typing import Any, Optional

import yaml

DEFAULT_CONFIG_PATHS = [
    "config.yaml",
    "jira2md.yaml",
]

BUILTIN_FIELDS = {
    "summary",
    "status",
    "assignee",
    "reporter",
    "priority",
    "issuetype",
    "created",
    "updated",
    "resolution",
    "labels",
    "components",
    "fixVersions",
    "description",
}


@dataclass
class JiraConfig:
    url: str = ""
    token: str = ""
    fields: dict[str, str] = field(default_factory=dict)


@dataclass
class OutputConfig:
    directory: str = "./export"
    filename_pattern: str = "{key}"
    fields: list[str] = field(
        default_factory=lambda: [
            "summary",
            "status",
            "assignee",
            "priority",
            "description",
        ]
    )
    include_comments: bool = False


@dataclass
class Config:
    jira: JiraConfig = field(default_factory=JiraConfig)
    output: OutputConfig = field(default_factory=OutputConfig)


def load_config(path: Optional[str] = None) -> Config:
    """Load configuration from a YAML file.

    Searches in order: explicit path, config.yaml, jira2md.yaml,
    ~/.config/jira2md/config.yaml.
    """
    config_path = _resolve_config_path(path)

    if config_path is None:
        # Return default config with env var token if available
        config = Config()
        config.jira.token = os.environ.get("JIRA2MD_TOKEN", "")
        return config

    with open(config_path) as f:
        data = yaml.safe_load(f) or {}

    return _parse_config(data)


def _resolve_config_path(explicit_path: Optional[str] = None) -> Optional[str]:
    if explicit_path:
        if not os.path.exists(explicit_path):
            print(f"Config file not found: {explicit_path}", file=sys.stderr)
            sys.exit(1)
        return explicit_path

    for p in DEFAULT_CONFIG_PATHS:
        if os.path.exists(p):
            return p

    home_config = os.path.join(
        os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config")),
        "jira2md",
        "config.yaml",
    )
    if os.path.exists(home_config):
        return home_config

    return None


def _parse_config(data: dict[str, Any]) -> Config:
    jira_data = data.get("jira", {})
    fields_data = jira_data.get("fields", {})
    output_data = data.get("output", {})

    token = jira_data.get("token", "") or os.environ.get("JIRA2MD_TOKEN", "")

    jira_config = JiraConfig(
        url=jira_data.get("url", ""),
        token=token,
        fields=fields_data,
    )

    output_config = OutputConfig(
        directory=output_data.get("directory", "./export"),
        filename_pattern=output_data.get("filename_pattern", "{key}"),
        fields=output_data.get("fields", OutputConfig().fields),
        include_comments=output_data.get("include_comments", False),
    )

    return Config(jira=jira_config, output=output_config)


def validate_config(config: Config) -> None:
    """Validate that required config values are present."""
    errors = []
    if not config.jira.url:
        errors.append("jira.url is required")
    if not config.jira.token:
        errors.append("jira.token is required (set in config or JIRA2MD_TOKEN env var)")
    if errors:
        for e in errors:
            print(f"Config error: {e}", file=sys.stderr)
        sys.exit(1)

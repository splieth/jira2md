import os
import tempfile

import yaml

from jira2md.config import _parse_config, load_config


def test_parse_config_minimal():
    # given
    data = {
        "jira": {
            "url": "https://jira.example.com",
            "token": "abc123",
        }
    }

    # when
    config = _parse_config(data)

    # then
    assert config.jira.url == "https://jira.example.com"
    assert config.jira.token == "abc123"
    assert config.jira.fields == {}
    assert config.output.directory == "./export"


def test_parse_config_full():
    # given
    data = {
        "jira": {
            "url": "https://jira.example.com",
            "token": "abc123",
            "fields": {
                "story_points": "customfield_10006",
                "acceptance_criteria": "customfield_10035",
            },
        },
        "output": {
            "directory": "./docs",
            "filename_pattern": "{key}",
            "fields": [
                "summary",
                "status",
                "story_points",
                "description",
            ],
        },
    }

    # when
    config = _parse_config(data)

    # then
    assert config.jira.fields["story_points"] == "customfield_10006"
    assert config.output.directory == "./docs"
    assert config.output.fields == [
        "summary",
        "status",
        "story_points",
        "description",
    ]


def test_parse_config_token_from_env(monkeypatch):
    # given
    monkeypatch.setenv("JIRA2MD_TOKEN", "env-token")
    data = {
        "jira": {
            "url": "https://jira.example.com",
        }
    }

    # when
    config = _parse_config(data)

    # then
    assert config.jira.token == "env-token"


def test_load_config_from_file():
    # given
    data = {
        "jira": {
            "url": "https://jira.example.com",
            "token": "file-token",
        }
    }
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(data, f)
        f.flush()
        path = f.name

    # when
    config = load_config(path)

    # then
    os.unlink(path)
    assert config.jira.url == "https://jira.example.com"
    assert config.jira.token == "file-token"

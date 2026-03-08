import argparse
import sys
from typing import Optional

from .config import Config, load_config, validate_config


def main(argv: Optional[list[str]] = None) -> None:
    parser = argparse.ArgumentParser(
        prog="jira2md",
        description="Export Jira issues to Markdown files",
    )
    parser.add_argument("--config", "-c", help="Path to config file")

    subparsers = parser.add_subparsers(dest="command")

    # export command
    export_parser = subparsers.add_parser("export", help="Export issues to Markdown")
    export_group = export_parser.add_mutually_exclusive_group(required=True)
    export_group.add_argument("--jql", help="JQL query to select issues")
    export_group.add_argument("--key", help="Single issue key (e.g. PROJ-123)")
    export_parser.add_argument(
        "--output-dir",
        "-o",
        help="Output directory (overrides config)",
    )
    export_parser.add_argument(
        "--max-results",
        type=int,
        default=50,
        help="Maximum number of issues to fetch (default: 50)",
    )

    # discover-fields command
    discover_parser = subparsers.add_parser(
        "discover-fields", help="Discover available Jira fields"
    )
    discover_parser.add_argument(
        "--search",
        "-s",
        help="Filter fields by name (case-insensitive)",
    )

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = load_config(args.config)

    if args.command == "export":
        _handle_export(args, config)
    elif args.command == "discover-fields":
        _handle_discover(args, config)


def _handle_export(args: argparse.Namespace, config: Config) -> None:
    validate_config(config)

    if args.output_dir:
        config.output.directory = args.output_dir

    from .client import connect, fetch_issue, fetch_issues
    from .renderer import export_issue, export_issues

    jira = connect(config.jira)

    if args.key:
        issue = fetch_issue(jira, args.key, config.jira)
        path = export_issue(issue, config.output)
        print(f"Exported: {path}")
    else:
        issues = fetch_issues(jira, args.jql, config.jira, args.max_results)
        if not issues:
            print("No issues found.")
            return
        paths = export_issues(issues, config.output)
        for p in paths:
            print(f"Exported: {p}")
        print(f"\n{len(paths)} issue(s) exported to {config.output.directory}")


def _handle_discover(args: argparse.Namespace, config: Config) -> None:
    validate_config(config)

    from .client import connect
    from .fields import discover_fields, print_fields

    jira = connect(config.jira)
    fields = discover_fields(jira, search=args.search)
    print_fields(fields)

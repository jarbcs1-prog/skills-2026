"""CLI tooling for the brainstorming skill."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from . import decision_matrix, spec_diff, validate_design_doc

_TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

_TEMPLATE_PLACEHOLDERS = {
    "Purpose": "<One sentence describing what this system does and why it exists.>",
    "Scope": "<What is in scope and what is explicitly out of scope.>",
    "Architecture": "<High-level architecture description.>",
    "Components": "<Component list with responsibilities and interfaces.>",
    "Data Flow": "<Describe how data moves through the system.>",
    "Error Handling": "<Describe error paths and how they are handled.>",
    "Testing": "<Describe the testing strategy.>",
    "Tradeoffs Considered": "<Tradeoffs evaluated and the decisions made.>",
}

_DECISIONS_TEMPLATE = """# Decision Matrix

## Options

<Comma-separated options, e.g. build, buy, partner.>

## Criteria

<Comma-separated criteria, e.g. cost, time, risk.>

## Weights

<Comma-separated weights summing to 1.0, e.g. 0.4, 0.3, 0.3.>
"""

_API_SERVICE_TEMPLATE = """# API Service Design

## Purpose

<What problem does this API solve? Who are the users?>

## Scope

<Endpoints, resources, and boundaries. What is explicitly out of scope?>

## Architecture

<REST, GraphQL, gRPC? How are routes organized? What middleware is used?>

## Components

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| <name> | <what it does> | <how it's called> |

## Data Flow

<Request lifecycle from client to storage and back.>

## Error Handling

<Error codes, error responses, retry logic, idempotency.>

## Testing

<Unit tests for handlers, integration tests for endpoints, contract tests.>

## Tradeoffs Considered

| Option | Selected? | Why |
|--------|-----------|-----|
| <option> | <yes/no> | <reason> |
"""

_CLI_TOOL_TEMPLATE = """# CLI Tool Design

## Purpose

<What does this CLI tool do? What problem does it solve?>

## Scope

<Commands, flags, and workflows. What is out of scope?>

## Architecture

<How is the tool structured? Commands, subcommands, configuration?>

## Components

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| <name> | <what it does> | <how it's called> |

## Data Flow

<How does data move through the tool?>

## Error Handling

<How are errors reported? Exit codes, error messages, logging?>

## Testing

<Unit tests for commands, integration tests for end-to-end workflows.>

## Tradeoffs Considered

| Option | Selected? | Why |
|--------|-----------|-----|
| <option> | <yes/no> | <reason> |
"""

_WEB_UI_TEMPLATE = """# Web UI Design

## Purpose

<What does this UI do? Who are the users?>

## Scope

<Pages, components, and user flows. What is out of scope?>

## Architecture

<SPA, SSR, SSG? Framework, routing, state management?>

## Components

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| <name> | <what it does> | <how it's called> |

## Data Flow

<How does data flow between the UI and backend?>

## Error Handling

<Error states, loading states, retry mechanisms.>

## Testing

<Unit tests for components, integration tests for user flows, E2E tests.>

## Tradeoffs Considered

| Option | Selected? | Why |
|--------|-----------|-----|
| <option> | <yes/no> | <reason> |
"""

_DATA_PIPELINE_TEMPLATE = """# Data Pipeline Design

## Purpose

<What data does this pipeline process? What is the output?>

## Scope

<Sources, transformations, and destinations. What is out of scope?>

## Architecture

<Batch or streaming? Orchestration framework? Schedule?>

## Components

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| <name> | <what it does> | <how it's called> |

## Data Flow

<How data moves from source through transformations to destination.>

## Error Handling

<Retry logic, dead letter queues, alerting on failures.>

## Testing

<Unit tests for transformations, integration tests for end-to-end pipelines.>

## Tradeoffs Considered

| Option | Selected? | Why |
|--------|-----------|-----|
| <option> | <yes/no> | <reason> |
"""

_LIBRARY_TEMPLATE = """# Library Design

## Purpose

<What problem does this library solve? Who are the users?>

## Scope

<Public API, modules, and extensions. What is out of scope?>

## Architecture

<Module structure, public vs internal APIs, extension points?>

## Components

| Component | Responsibility | Interface |
|-----------|---------------|-----------|
| <name> | <what it does> | <how it's called> |

## Data Flow

<How users interact with the library and data moves through it.>

## Error Handling

<Error types, exception hierarchy, user-facing error messages.>

## Testing

<Unit tests for all public APIs, property-based tests, documentation examples.>

## Tradeoffs Considered

| Option | Selected? | Why |
|--------|-----------|-----|
| <option> | <yes/no> | <reason> |
"""

_DECISIONS_TEMPLATE = """# Decision Matrix

## Options

<Comma-separated options, e.g. build, buy, partner.>

## Criteria

<Comma-separated criteria, e.g. cost, time, risk.>

## Weights

<Comma-separated weights summing to 1.0, e.g. 0.4, 0.3, 0.3.>
"""


def _design_doc_template() -> str:
    sections = "\n\n".join(
        f"## {name}\n\n{_TEMPLATE_PLACEHOLDERS[name]}"
        for name in validate_design_doc.REQUIRED_SECTIONS
    )
    return f"# <Project Title> - Design\n\n{sections}\n"


def _error(message: str) -> int:
    print(message)
    return 1


def _error_json(message: str) -> int:
    print(json.dumps({"error": message}))
    return 1


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _handle_init(args) -> int:
    """Initialize a brainstorming project structure."""
    project_dir = Path.cwd()
    docs_dir = project_dir / "docs" / "specs"
    templates_dir = project_dir / "templates"

    # Create directories
    docs_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)

    # Generate initial design doc from template
    template_type = args.template
    if template_type == "design-doc":
        text = _design_doc_template()
    elif template_type == "decisions":
        text = _DECISIONS_TEMPLATE
    elif template_type == "api-service":
        text = _API_SERVICE_TEMPLATE
    elif template_type == "cli-tool":
        text = _CLI_TOOL_TEMPLATE
    elif template_type == "web-ui":
        text = _WEB_UI_TEMPLATE
    elif template_type == "data-pipeline":
        text = _DATA_PIPELINE_TEMPLATE
    elif template_type == "library":
        text = _LIBRARY_TEMPLATE
    else:
        return _error_json(f"unknown template type: {template_type}")

    # Write template file
    template_file = templates_dir / f"{template_type}-template.md"
    template_file.write_text(text, encoding="utf-8")

    # Write a README for the templates directory
    readme_file = templates_dir / "README.md"
    if not readme_file.exists():
        readme_file.write_text(
            "# Templates\n\n"
            "Design doc templates for common project types.\n\n"
            "| Template | Description |\n"
            "|----------|-------------|\n"
            "| design-doc | General design document |\n"
            "| api-service | REST/GraphQL API service |\n"
            "| cli-tool | Command-line tool |\n"
            "| web-ui | Web user interface |\n"
            "| data-pipeline | Data processing pipeline |\n"
            "| library | Reusable library/package |\n",
            encoding="utf-8"
        )

    print(f"✅ Initialized brainstorming project structure.")
    print(f"   Templates: {templates_dir}")
    print(f"   Specs directory: {docs_dir}")
    print(f"   Generated: {template_file.name}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="brainstorming", description="CLI tooling for the brainstorming skill."
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Validate a design doc has all required sections.")
    p_validate.add_argument("design_doc", metavar="design-doc.md")

    p_decide = sub.add_parser("decide", help="Score options against weighted criteria.")
    p_decide.add_argument("--criteria", required=True)
    p_decide.add_argument("--weights", required=True)
    p_decide.add_argument("--options", required=True)

    p_template = sub.add_parser("template", help="Print a design-doc or decision-matrix template.")
    p_template.add_argument("--type", required=True, choices=[
        "design-doc", "decisions", "api-service", "cli-tool", "web-ui", "data-pipeline", "library"
    ])
    p_template.add_argument("--output", default=None)

    p_init = sub.add_parser("init", help="Initialize a brainstorming project structure.")
    p_init.add_argument("--template", choices=["design-doc", "decisions", "api-service", "cli-tool", "web-ui", "data-pipeline", "library"], default="design-doc")
    p_init.add_argument("--output", "-o", default=None, help="Output directory for generated files")

    p_diff = sub.add_parser("diff", help="Compare section headings between two design docs.")
    p_diff.add_argument("--base", required=True)
    p_diff.add_argument("--target", required=True)

    args = parser.parse_args()

    if args.command == "validate":
        try:
            result = validate_design_doc.validate_design_doc(Path(args.design_doc))
        except OSError as exc:
            return _error(f"cannot read {args.design_doc}: {exc}")
        print(json.dumps(result, indent=2))
        return 0 if result["valid"] else 1

    if args.command == "decide":
        options = _split_csv(args.options)
        criteria = _split_csv(args.criteria)
        try:
            weights = [float(item) for item in _split_csv(args.weights)]
        except ValueError as exc:
            return _error_json(f"invalid weights: {exc}")
        if len(criteria) != len(weights):
            return _error_json(
                f"criteria/weights length mismatch: {len(criteria)} != {len(weights)}"
            )
        result = decision_matrix.evaluate(options, criteria, weights)
        print(json.dumps(result, indent=2))
        return 0

    if args.command == "template":
        if args.type == "design-doc":
            text = _design_doc_template()
        elif args.type == "decisions":
            text = _DECISIONS_TEMPLATE
        elif args.type == "api-service":
            text = _API_SERVICE_TEMPLATE
        elif args.type == "cli-tool":
            text = _CLI_TOOL_TEMPLATE
        elif args.type == "web-ui":
            text = _WEB_UI_TEMPLATE
        elif args.type == "data-pipeline":
            text = _DATA_PIPELINE_TEMPLATE
        elif args.type == "library":
            text = _LIBRARY_TEMPLATE
        else:
            return _error_json(f"unknown template type: {args.type}")
        if args.output:
            Path(args.output).write_text(text, encoding="utf-8")
        else:
            print(text, end="")
        return 0

    if args.command == "init":
        return _handle_init(args)

    if args.command == "diff":
        try:
            result = spec_diff.diff_design_docs(Path(args.base), Path(args.target))
        except OSError as exc:
            return _error_json(f"cannot read design doc: {exc}")
        print(json.dumps(result, indent=2))
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())

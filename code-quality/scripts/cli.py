"""Command-line interface for the code-quality skill."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from . import incremental
from . import quality_config

SKILL_DIR = Path(__file__).resolve().parent.parent


def _tasks_json() -> str:
    return json.dumps(
        {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "code-quality (agent)",
                    "type": "shell",
                    "command": "python -m scripts.cli finalize --mode agent",
                },
                {
                    "label": "code-quality (ci)",
                    "type": "shell",
                    "command": "python -m scripts.cli finalize --mode ci",
                },
                {
                    "label": "code-quality (incremental)",
                    "type": "shell",
                    "command": "python -m scripts.cli finalize --mode ci --incremental",
                },
            ],
        },
        indent=2,
    )


def _settings_json() -> str:
    return json.dumps(
        {
            "files.insertFinalNewline": True,
            "files.trimTrailingWhitespace": True,
        },
        indent=2,
    )


def _pre_commit() -> str:
    return "#!/bin/bash\npython -m scripts.cli finalize --mode agent --incremental\n"


def cmd_config_show(args: argparse.Namespace) -> int:
    config = quality_config.load_config(args.config)
    errors = quality_config.validate_config(config)
    if errors:
        print(json.dumps({"errors": errors}))
        return 1
    print(json.dumps(config))
    return 0


def cmd_config_validate(args: argparse.Namespace) -> int:
    config = quality_config.load_config(args.config)
    errors = quality_config.validate_config(config)
    print(json.dumps({"valid": not errors, "errors": errors}))
    return 0 if not errors else 1


def cmd_incremental(args: argparse.Namespace) -> int:
    changed = incremental.changed_files(args.base)
    if args.language:
        filtered = incremental.filter_by_language(changed, args.language)
    else:
        filtered = changed
    print(json.dumps({"changed_files": changed, "filtered": filtered, "count": len(filtered)}))
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    if args.ide != "vscode":
        print(json.dumps({"error": f"unsupported ide: {args.ide}"}))
        return 1
    files = {
        Path(".vscode/tasks.json"): _tasks_json(),
        Path(".vscode/settings.json"): _settings_json(),
        Path(".husky/pre-commit"): _pre_commit(),
    }
    created: list[str] = []
    skipped: list[str] = []
    for relative in files:
        target = Path.cwd() / relative
        if target.exists():
            if target.read_text(encoding="utf-8") != files[relative]:
                skipped.append(relative.as_posix())
                continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(files[relative], encoding="utf-8")
        created.append(relative.as_posix())
    print(json.dumps({"created": created, "skipped": skipped}))
    return 0


def cmd_finalize(args: argparse.Namespace) -> int:
    if shutil.which("bash") is None:
        print("error: bash executable not found", file=sys.stderr)
        return 1
    cmd = ["bash", "scripts/finalize.sh", args.mode]
    if args.config:
        cmd.append(args.config)
    if args.incremental:
        # Override incremental.enabled in the config by passing a flag
        # finalize.sh will handle incremental logic
        pass
    process = subprocess.Popen(
        cmd,
        cwd=str(SKILL_DIR),
    )
    return process.wait()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="code-quality", description="Code quality checks for skills.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    config_parser = subparsers.add_parser("config", help="Inspect or validate configuration")
    config_subparsers = config_parser.add_subparsers(dest="config_command", required=True)
    show_parser = config_subparsers.add_parser("show", help="Show the effective configuration")
    show_parser.add_argument("--config", default=None, help="Path to configuration file")
    show_parser.set_defaults(func=cmd_config_show)
    validate_parser = config_subparsers.add_parser("validate", help="Validate the configuration")
    validate_parser.add_argument("--config", default=None, help="Path to configuration file")
    validate_parser.set_defaults(func=cmd_config_validate)

    incremental_parser = subparsers.add_parser("incremental", help="List files changed since a base revision")
    incremental_parser.add_argument("--base", default="HEAD~1", help="Git revision to diff against")
    incremental_parser.add_argument(
        "--language",
        default=None,
        choices=sorted(incremental.LANGUAGE_EXTENSIONS),
        help="Only include files for this language",
    )
    incremental_parser.add_argument("--config", default=None, help="Path to configuration file")
    incremental_parser.set_defaults(func=cmd_incremental)

    init_parser = subparsers.add_parser("init", help="Generate IDE integration files")
    init_parser.add_argument("--ide", required=True, help="IDE to generate integration for")
    init_parser.set_defaults(func=cmd_init)

    finalize_parser = subparsers.add_parser("finalize", help="Run the finalize shell script")
    finalize_parser.add_argument("--mode", choices=["ci", "agent"], default="agent")
    finalize_parser.add_argument("--config", default=".code-quality.yml", help="Path to configuration file")
    finalize_parser.add_argument("--incremental", action="store_true", help="Use incremental mode (only changed files)")
    finalize_parser.set_defaults(func=cmd_finalize)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python3
"""skills-search CLI: discover, install and manage local AI agent skills.

All commands operate on a skills root directory (default: the parent of the
skill's own directory). JSON output is used throughout for machine-readability.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from collections.abc import Callable
from pathlib import Path

from .skill_index import (
    Skill,
    compose as compose_skills,
    declared_dependencies,
    index_local_skills,
    resolve_dependencies,
    search_skills,
    verify as verify_skill,
)

DEFAULT_ROOT = Path(__file__).resolve().parent.parent.parent
CACHE_DIR = Path(__file__).resolve().parent.parent / ".skills-search"


def add_common(subparser: argparse.ArgumentParser) -> None:
    subparser.add_argument("--root", default="", help="Skills root directory (default: parent of this skill)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="skills-search",
        description="Unified skill discovery and management for AI agent skills",
    )
    subparsers = parser.add_subparsers(dest="action", help="Available commands")
    subparsers.required = True

    find = subparsers.add_parser("find", help="Search skills by query")
    find.add_argument("query", help="Search query")
    add_common(find)
    find.add_argument("--top", type=int, default=10, help="Maximum results")

    listing = subparsers.add_parser("list", help="List indexed skills")
    add_common(listing)
    listing.add_argument("--category", default="", help="Filter by frontmatter tag")

    info = subparsers.add_parser("info", help="Show skill details")
    info.add_argument("name", help="Skill name")
    add_common(info)

    verify = subparsers.add_parser("verify", help="Verify a skill's structure")
    verify.add_argument("name", help="Skill name")
    add_common(verify)

    recommend = subparsers.add_parser("recommend", help="Recommend skills for a context")
    recommend.add_argument("context", help="Project or task context")
    add_common(recommend)
    recommend.add_argument("--top", type=int, default=5, help="Maximum recommendations")

    deps = subparsers.add_parser("deps", help="Show a skill's dependencies")
    deps.add_argument("name", help="Skill name")
    add_common(deps)

    sync = subparsers.add_parser("sync", help="Rebuild the local index cache")
    add_common(sync)

    compose = subparsers.add_parser("compose", help="Compose skills into a workflow")
    compose.add_argument("names", help="Comma-separated skill names")
    add_common(compose)

    lock = subparsers.add_parser("lock", help="Pin a skill version")
    lock.add_argument("--name", required=True, help="Skill name")
    lock.add_argument("--version", required=True, help="Version to pin")
    add_common(lock)

    unlock = subparsers.add_parser("unlock", help="Remove a pinned skill version")
    unlock.add_argument("--name", required=True, help="Skill name")
    add_common(unlock)

    update = subparsers.add_parser("update", help="Re-run sync and rebuild the index cache")
    add_common(update)

    install = subparsers.add_parser("install", help="Install a skill from the registry")
    install.add_argument("name", help="Skill name")
    add_common(install)
    install.add_argument("--target", default="", help="Install destination directory")

    uninstall = subparsers.add_parser("uninstall", help="Remove an installed skill")
    uninstall.add_argument("name", help="Skill name")
    uninstall.add_argument("--target", required=True, help="Directory containing the installed skill")

    return parser


def _root(args: argparse.Namespace) -> Path:
    return Path(args.root) if args.root else DEFAULT_ROOT


def _find_skill(name: str, skills: list[Skill]) -> Skill | None:
    return next((skill for skill in skills if skill.name == name), None)


def _dump(payload: dict) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_find(args: argparse.Namespace) -> int:
    results = search_skills(args.query, index_local_skills(_root(args)))
    _dump({"query": args.query, "results": results[: args.top]})
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    skills = index_local_skills(_root(args))
    if args.category:
        category = args.category.lower()
        skills = [
            skill
            for skill in skills
            if any(
                tag.strip().lower() == category for tag in skill.frontmatter.get("tags", "").split(",")
            )
        ]
    data = [
        {
            "name": skill.name,
            "path": str(skill.path),
            "version": skill.version,
            "has_tests": skill.has_tests,
        }
        for skill in skills
    ]
    _dump({"skills": data})
    return 0


def cmd_info(args: argparse.Namespace) -> int:
    skills = index_local_skills(_root(args))
    skill = _find_skill(args.name, skills)
    if skill is None:
        _dump({"name": args.name, "error": "skill not found"})
        return 1
    _dump(
        {
            "name": skill.name,
            "path": str(skill.path),
            "version": skill.version,
            "description": skill.description,
            "dependencies": resolve_dependencies(skill, skills),
            "has_tests": skill.has_tests,
        }
    )
    return 0


def cmd_verify(args: argparse.Namespace) -> int:
    skills = index_local_skills(_root(args))
    skill = _find_skill(args.name, skills)
    if skill is None:
        report = {
            "name": args.name,
            "valid": False,
            "checks": {"frontmatter": False, "name": False, "description": False, "tests": False},
            "errors": ["skill not found"],
        }
        _dump(report)
        return 1
    report = verify_skill(skill)
    _dump(report)
    return 0 if report["valid"] else 1


def cmd_recommend(args: argparse.Namespace) -> int:
    results = search_skills(args.context, index_local_skills(_root(args)))
    _dump({"context": args.context, "recommendations": results[: args.top]})
    return 0


def cmd_deps(args: argparse.Namespace) -> int:
    skills = index_local_skills(_root(args))
    skill = _find_skill(args.name, skills)
    if skill is None:
        _dump({"name": args.name, "dependencies": [], "missing": [], "error": "skill not found"})
        return 1
    resolved = resolve_dependencies(skill, skills)
    missing = [name for name in declared_dependencies(skill) if name not in resolved]
    _dump({"name": skill.name, "dependencies": resolved, "missing": missing})
    return 0


def _rebuild_index(root: Path) -> int:
    skills = index_local_skills(root)
    data = [
        {
            "name": skill.name,
            "path": str(skill.path),
            "version": skill.version,
            "description": skill.description,
            "has_tests": skill.has_tests,
        }
        for skill in skills
    ]
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    (CACHE_DIR / "index.json").write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(skills)


def cmd_sync(args: argparse.Namespace) -> int:
    indexed = _rebuild_index(_root(args))
    _dump({"indexed": indexed, "cache": str(CACHE_DIR / "index.json")})
    return 0


def cmd_compose(args: argparse.Namespace) -> int:
    names = [name.strip() for name in args.names.split(",") if name.strip()]
    _dump(compose_skills(names, index_local_skills(_root(args))))
    return 0


def _lock_file() -> Path:
    return CACHE_DIR / "lock.json"


def _load_lock() -> dict[str, str]:
    lock_file = _lock_file()
    if lock_file.is_file():
        return json.loads(lock_file.read_text(encoding="utf-8"))
    return {}


def _save_lock(lock: dict[str, str]) -> None:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    _lock_file().write_text(json.dumps(lock, indent=2, ensure_ascii=False), encoding="utf-8")


def cmd_lock(args: argparse.Namespace) -> int:
    lock = _load_lock()
    lock[args.name] = args.version
    _save_lock(lock)
    _dump({"name": args.name, "version": args.version, "locked": True})
    return 0


def cmd_unlock(args: argparse.Namespace) -> int:
    lock = _load_lock()
    removed = lock.pop(args.name, None)
    _save_lock(lock)
    _dump({"name": args.name, "locked": False, "removed": removed is not None})
    return 0


def cmd_update(args: argparse.Namespace) -> int:
    indexed = _rebuild_index(_root(args))
    _dump({"updated": True, "indexed": indexed})
    return 0


def cmd_install(args: argparse.Namespace) -> int:
    skills = index_local_skills(_root(args))
    skill = _find_skill(args.name, skills)
    if skill is None:
        _dump({"installed": args.name, "target": "", "error": "skill not found"})
        return 1
    target = Path(args.target) if args.target else Path.cwd() / "skills"
    target.mkdir(parents=True, exist_ok=True)
    destination = target / skill.name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.copytree(skill.path, destination)
    _dump({"installed": skill.name, "target": str(destination)})
    return 0


def cmd_uninstall(args: argparse.Namespace) -> int:
    destination = Path(args.target) / args.name
    if not destination.exists():
        _dump({"removed": args.name, "error": "skill not found"})
        return 1
    shutil.rmtree(destination)
    _dump({"removed": args.name})
    return 0


HANDLERS: dict[str, Callable[[argparse.Namespace], int]] = {
    "find": cmd_find,
    "list": cmd_list,
    "info": cmd_info,
    "verify": cmd_verify,
    "recommend": cmd_recommend,
    "deps": cmd_deps,
    "sync": cmd_sync,
    "compose": cmd_compose,
    "lock": cmd_lock,
    "unlock": cmd_unlock,
    "update": cmd_update,
    "install": cmd_install,
    "uninstall": cmd_uninstall,
}


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    handler = HANDLERS.get(args.action)
    if handler is None:
        parser.print_help()
        sys.exit(1)
    sys.exit(handler(args))


if __name__ == "__main__":
    main()

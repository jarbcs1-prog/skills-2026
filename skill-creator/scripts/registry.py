"""Local skill registry: publish, resolve, install and dependency resolution.

Self-contained (stdlib only). A registry is a directory holding an
``index.json`` plus one subdirectory per skill/version::

    registry/
      index.json
      my-skill/
        1.0.0/
          SKILL.md
          skill.yaml
          ...
"""

from __future__ import annotations

import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

_SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

_IGNORE_DIRS = {"__pycache__", "node_modules", ".git", ".pytest_cache", ".ruff_cache"}
_IGNORE_FILES = {"*.pyc", "*.pyo"}


def _ignore(directory: str, names: list[str]) -> set[str]:
    return {
        name
        for name in names
        if name in _IGNORE_DIRS
        or any(Path(name).match(pattern) for pattern in _IGNORE_FILES)
    }


def parse_version(version: str) -> tuple[int, int, int]:
    """Parse a semantic version into a comparable tuple."""
    match = _SEMVER_RE.match(version.strip())
    if not match:
        raise ValueError(f"invalid version {version!r}; expected MAJOR.MINOR.PATCH")
    return tuple(int(part) for part in match.groups())


def bump_version(version: str, part: str) -> str:
    """Bump major, minor or patch of ``version``."""
    major, minor, patch = parse_version(version)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"unknown bump part {part!r}; use major, minor or patch")


def compare_versions(a: str, b: str) -> int:
    """Compare two versions: -1, 0 or 1."""
    return (parse_version(a) > parse_version(b)) - (
        parse_version(a) < parse_version(b)
    )


@dataclass
class PublishResult:
    """Result of a publish operation."""

    published: bool
    name: str
    version: str
    message: str

    def summary(self) -> str:
        return self.message


@dataclass
class InstallResult:
    """Result of an install operation."""

    installed: bool
    name: str
    version: str
    target: str
    message: str

    def summary(self) -> str:
        return self.message


def _read_manifest(skill_path: Path) -> dict[str, object]:
    manifest_path = skill_path / "skill.yaml"
    if not manifest_path.exists():
        return {}
    manifest: dict[str, object] = {}
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        key, sep, value = line.partition(":")
        if not sep:
            continue
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            try:
                manifest[key] = json.loads(value)
            except json.JSONDecodeError:
                manifest[key] = value
        else:
            manifest[key] = value
    return manifest


class SkillRegistry:
    """A local directory-backed skill registry."""

    def __init__(self, registry_dir: str | Path) -> None:
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.registry_dir / "index.json"
        if self.index_path.exists():
            self.index = json.loads(self.index_path.read_text(encoding="utf-8"))
        else:
            self.index: dict[str, list[str]] = {}

    def _save_index(self) -> None:
        self.index_path.write_text(
            json.dumps(self.index, indent=2), encoding="utf-8"
        )

    def available_versions(self, name: str) -> list[str]:
        versions = self.index.get(name, [])
        return sorted(versions, key=parse_version)

    def resolve(self, spec: str) -> tuple[str, str]:
        """Resolve ``name`` or ``name@version`` to (name, version)."""
        if "@" in spec:
            name, _, version = spec.partition("@")
            if not name or not version:
                raise ValueError(f"invalid spec {spec!r}; expected name@version")
            return name, version
        versions = self.available_versions(spec)
        if not versions:
            raise ValueError(f"skill {spec!r} not found in registry")
        return spec, versions[-1]

    def publish(
        self, skill_path: str | Path, version: str | None = None
    ) -> PublishResult:
        """Publish a skill directory into the registry."""
        source = Path(skill_path)
        if not (source / "SKILL.md").exists():
            return PublishResult(
                published=False, name=source.name, version="", message="ERROR: no SKILL.md"
            )

        manifest = _read_manifest(source)
        name = str(manifest.get("name") or source.name)
        try:
            version = version or str(manifest.get("version") or "1.0.0")
            parse_version(version)
        except ValueError as exc:
            return PublishResult(published=False, name=name, version="", message=str(exc))

        versions = self.available_versions(name)
        if version in versions:
            return PublishResult(
                published=False,
                name=name,
                version=version,
                message=f"ERROR: {name}@{version} already published",
            )

        dest = self.registry_dir / name / version
        if dest.exists():
            return PublishResult(
                published=False,
                name=name,
                version=version,
                message=f"ERROR: destination {dest} already exists",
            )
        dest.mkdir(parents=True, exist_ok=False)
        shutil.copytree(source, dest, ignore=_ignore, dirs_exist_ok=True)

        if name not in self.index:
            self.index[name] = []
        self.index[name].append(version)
        self._save_index()
        return PublishResult(
            published=True,
            name=name,
            version=version,
            message=f"Published {name}@{version}",
        )

    def install(
        self, spec: str, target_dir: str | Path = "."
    ) -> InstallResult:
        """Install a skill from the registry into ``target_dir``."""
        try:
            name, version = self.resolve(spec)
        except ValueError as exc:
            return InstallResult(
                installed=False, name=spec, version="", target=str(target_dir), message=str(exc)
            )

        source = self.registry_dir / name / version
        if not source.exists():
            return InstallResult(
                installed=False,
                name=name,
                version=version,
                target=str(target_dir),
                message=f"ERROR: {name}@{version} is missing from registry",
            )

        dest = Path(target_dir) / name
        if dest.exists():
            return InstallResult(
                installed=False,
                name=name,
                version=version,
                target=str(target_dir),
                message=f"ERROR: {dest} already exists",
            )
        shutil.copytree(source, dest, ignore=_ignore)
        if not (dest / "SKILL.md").exists():
            shutil.rmtree(dest)
            return InstallResult(
                installed=False,
                name=name,
                version=version,
                target=str(target_dir),
                message="ERROR: installed skill is missing SKILL.md",
            )
        return InstallResult(
            installed=True,
            name=name,
            version=version,
            target=str(target_dir),
            message=f"Installed {name}@{version} to {dest}",
        )

    def resolve_dependencies(self, skill_path: str | Path) -> list[str]:
        """Resolve dependency names leaf-first (DFS with cycle detection)."""
        root = Path(skill_path)
        manifest = _read_manifest(root)
        dependencies = manifest.get("dependencies", [])
        if not isinstance(dependencies, list):
            dependencies = []
        ordered: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def _walk(name: str) -> None:
            if name in visited:
                return
            if name in visiting:
                raise ValueError(f"dependency cycle detected at {name!r}")
            visiting.add(name)
            dep_source = self.registry_dir / name
            if dep_source.exists():
                child_manifest = _read_manifest(dep_source)
                for child in child_manifest.get("dependencies", []):
                    if isinstance(child, str):
                        _walk(child)
            if name not in visited:
                visited.add(name)
                ordered.append(name)
            visiting.discard(name)

        for dependency in dependencies:
            if isinstance(dependency, str):
                _walk(dependency)
        return ordered


def main() -> None:
    if len(sys.argv) < 3:
        print("usage: python scripts/registry.py <publish|install> ...")
        sys.exit(1)

    command = sys.argv[1]
    registry_dir = sys.argv[2]
    registry = SkillRegistry(registry_dir)

    if command == "publish":
        if len(sys.argv) < 4:
            print("usage: python scripts/registry.py <registry_dir> publish <skill_path> [version]")
            sys.exit(1)
        result = registry.publish(sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else None)
        print(result.summary())
        sys.exit(0 if result.published else 1)

    if command == "install":
        if len(sys.argv) < 4:
            print("usage: python scripts/registry.py <registry_dir> install <spec> [target_dir]")
            sys.exit(1)
        target = sys.argv[5] if len(sys.argv) > 4 else "."
        result = registry.install(sys.argv[3], target)
        print(result.summary())
        sys.exit(0 if result.installed else 1)

    print(f"unknown command {command!r}")
    sys.exit(1)


if __name__ == "__main__":
    main()

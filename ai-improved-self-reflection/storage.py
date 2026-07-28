"""
AI Self-Reflection Engine v2

Storage layer.

Responsible for:

- JSON persistence
- memory initialization
- safe loading
- serialization
- recovery from malformed files

Storage should never contain business logic.
"""

import json
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, List


BASE_DIR = Path(__file__).resolve().parent

MEMORY_DIR = BASE_DIR / "memory"


REFLECTION_MEMORY = (
    MEMORY_DIR / "reflection_events.json"
)

CANDIDATE_MEMORY = (
    MEMORY_DIR / "candidate_lessons.json"
)

CAPABILITY_MEMORY = (
    MEMORY_DIR / "capabilities_memory.json"
)

VALIDATION_MEMORY = (
    MEMORY_DIR / "validation_history.json"
)

FRICTION_LOG = (
    MEMORY_DIR / "friction_log.md"
)


DEFAULT_MEMORY_FILES = {
    REFLECTION_MEMORY: [],
    CANDIDATE_MEMORY: [],
    CAPABILITY_MEMORY: {
        "capabilities": [],
        "candidate_lessons": [],
        "deprecated_patterns": [],
    },
    VALIDATION_MEMORY: [],
}


def ensure_memory_directory() -> None:
    """
    Creates memory directory and missing files.
    """

    MEMORY_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for path, default in DEFAULT_MEMORY_FILES.items():
        if not path.exists():
            save_json(
                path,
                default,
            )


def load_json(
    path: Path,
    default: Any = None,
) -> Any:
    """
    Safely load JSON.

    Returns default if:

    - file does not exist
    - file is empty
    - JSON is malformed
    """

    if not path.exists():
        return default

    try:
        with path.open(
            "r",
            encoding="utf-8",
        ) as file:
            content = file.read().strip()

            if not content:
                return default

            return json.loads(content)

    except (
        json.JSONDecodeError,
        OSError,
    ):
        return default


def save_json(
    path: Path,
    data: Any,
) -> None:
    """
    Save JSON with consistent formatting.
    """

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
        )


def serialize(
    item: Any,
) -> Any:
    """
    Convert dataclasses into JSON-compatible structures.
    """

    if is_dataclass(item):
        return asdict(item)

    if isinstance(item, list):
        return [
            serialize(element)
            for element in item
        ]

    if isinstance(item, dict):
        return {
            key: serialize(value)
            for key, value in item.items()
        }

    return item


def append_json_record(
    path: Path,
    record: Any,
) -> None:
    """
    Append a record to a JSON list file.
    """

    existing = load_json(
        path,
        [],
    )

    if not isinstance(existing, list):
        existing = []

    existing.append(
        serialize(record)
    )

    save_json(
        path,
        existing,
    )


def update_json(
    path: Path,
    data: Any,
) -> None:
    """
    Explicit replacement save.

    Used when updating capability memory
    rather than appending events.
    """

    save_json(
        path,
        serialize(data),
    )


def initialize_friction_log() -> None:
    """
    Creates human-readable reflection log.
    """

    if FRICTION_LOG.exists():
        return

    FRICTION_LOG.write_text(
        """# Friction Log

## Purpose

This file records reflection events that may
contribute to future capability improvement.

A reflection event is not a failure report.

It is an observation about the relationship
between:

- chosen approach
- task requirements
- resulting outcome

---

# Reflection Lifecycle

Observation
↓
Diagnosis
↓
Generalization
↓
Validation
↓
Capability Update

---

""",
        encoding="utf-8",
    )


def append_markdown(
    entry: str,
) -> None:
    """
    Add human-readable reflection entry.
    """

    initialize_friction_log()

    with FRICTION_LOG.open(
        "a",
        encoding="utf-8",
    ) as file:
        file.write(
            entry
        )


def initialize_storage() -> None:
    """
    Prepare all persistent storage.
    """

    ensure_memory_directory()

    initialize_friction_log()

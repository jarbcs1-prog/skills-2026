"""
Tests for storage module.
"""

import sys
import os
import json
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from storage import (
    load_json,
    save_json,
    serialize,
    append_json_record,
    initialize_storage,
    MEMORY_DIR,
    DEFAULT_MEMORY_FILES,
)


def test_load_json_nonexistent():
    result = load_json(Path("nonexistent.json"), default=[])
    assert result == []
    print("PASS: load_json nonexistent")


def test_load_json_empty():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("")
        temp_path = Path(f.name)
    
    result = load_json(temp_path, default=[])
    assert result == []
    temp_path.unlink()
    print("PASS: load_json empty")


def test_load_json_valid():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([1, 2, 3], f)
        temp_path = Path(f.name)
    
    result = load_json(temp_path, default=[])
    assert result == [1, 2, 3]
    temp_path.unlink()
    print("PASS: load_json valid")


def test_save_json():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = Path(f.name)
    
    save_json(temp_path, {"key": "value"})
    result = load_json(temp_path)
    assert result == {"key": "value"}
    temp_path.unlink()
    print("PASS: save_json")


def test_serialize_dataclass():
    from models import CommunicationAudit
    
    audit = CommunicationAudit(corrections=2)
    result = serialize(audit)
    assert isinstance(result, dict)
    assert result["corrections"] == 2
    print("PASS: serialize dataclass")


def test_serialize_list():
    from models import CommunicationAudit
    
    audit = CommunicationAudit(corrections=1)
    result = serialize([audit, {"key": "value"}])
    assert isinstance(result, list)
    assert result[0]["corrections"] == 1
    assert result[1] == {"key": "value"}
    print("PASS: serialize list")


def test_append_json_record():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump([], f)
        temp_path = Path(f.name)
    
    append_json_record(temp_path, {"test": "record"})
    result = load_json(temp_path)
    assert len(result) == 1
    assert result[0]["test"] == "record"
    temp_path.unlink()
    print("PASS: append_json_record")


def test_ensure_memory_directory():
    test_dir = Path(tempfile.mkdtemp())
    original_memory_dir = MEMORY_DIR
    original_default_files = DEFAULT_MEMORY_FILES.copy()
    
    try:
        import storage
        new_memory_dir = test_dir / "memory"
        storage.MEMORY_DIR = new_memory_dir
        
        new_default_files = {
            new_memory_dir / "reflections.json": [],
            new_memory_dir / "candidate_lessons.json": [],
            new_memory_dir / "capabilities_memory.json": {
                "capabilities": [],
                "candidate_lessons": [],
                "deprecated_patterns": [],
            },
            new_memory_dir / "validation_history.json": [],
        }
        storage.DEFAULT_MEMORY_FILES = new_default_files
        
        initialize_storage()
        
        assert new_memory_dir.exists()
        assert (new_memory_dir / "reflections.json").exists()
        assert (new_memory_dir / "capabilities_memory.json").exists()
    finally:
        storage.MEMORY_DIR = original_memory_dir
        storage.DEFAULT_MEMORY_FILES = original_default_files
        shutil.rmtree(test_dir)
    print("PASS: ensure_memory_directory")


if __name__ == "__main__":
    test_load_json_nonexistent()
    test_load_json_empty()
    test_load_json_valid()
    test_save_json()
    test_serialize_dataclass()
    test_serialize_list()
    test_append_json_record()
    test_ensure_memory_directory()
    print("\nAll storage tests passed!")

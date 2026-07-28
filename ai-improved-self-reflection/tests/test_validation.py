"""
Tests for validation module.
"""

import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pathlib import Path
from validation import (
    calculate_validation_score,
    get_capability_validations,
)
from storage import load_json


def test_calculate_validation_score_no_records():
    score = calculate_validation_score("nonexistent")
    assert score == 0.5
    print("PASS: calculate_validation_score empty")


def test_get_capability_validations_empty():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        import json
        json.dump([], f)
        temp_path = Path(f.name)
    
    from storage import VALIDATION_MEMORY
    import storage
    original = storage.VALIDATION_MEMORY
    storage.VALIDATION_MEMORY = temp_path
    
    result = get_capability_validations("nonexistent")
    assert result == []
    
    storage.VALIDATION_MEMORY = original
    temp_path.unlink()
    print("PASS: get_capability_validations empty")


if __name__ == "__main__":
    test_calculate_validation_score_no_records()
    test_get_capability_validations_empty()
    print("\nAll validation tests passed!")

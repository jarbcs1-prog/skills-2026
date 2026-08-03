"""
Test Compaction Reversibility — Test all compaction strategies for lossless restore.
"""

import json
import tempfile
import os
from typing import List, Dict, Any

from compaction import (
    Compactor, CompactionConfig, CompactionStrategy,
    TokenBudgetCompactor, AgeBasedCompactor, ImportanceBasedCompactor, HybridCompactor,
    TimestampHidingCompactor, HeadTailProtectionCompactor,
    RepeatedToolPruningCompactor, ErrorPreservationCompactor,
)


def create_test_context() -> List[Dict[str, Any]]:
    """Create a realistic test context with various entry types."""
    return [
        {"type": "system_prompt", "content": "You are a helpful assistant."},
        {"type": "user_message", "content": "Help me refactor this code.", "role": "user"},
        {"type": "tool_call", "tool": "read_file", "arguments": {"path": "src/main.py"}, "output": "def main():\n    print('hello')\n    return 0\n" * 100},
        {"type": "assistant_message", "content": "I'll help you refactor that code."},
        {"type": "tool_call", "tool": "edit_file", "arguments": {"path": "src/main.py", "old": "print('hello')", "new": "print('world')"}, "output": "File updated successfully."},
        {"type": "tool_call", "tool": "read_file", "arguments": {"path": "src/main.py"}, "output": "def main():\n    print('world')\n    return 0\n" * 100},
        {"type": "user_message", "content": "Now add error handling.", "role": "user"},
        {"type": "tool_call", "tool": "edit_file", "arguments": {"path": "src/main.py", "old": "return 0", "new": "try:\n    return 0\nexcept Exception:\n    return 1"}, "output": "File updated with error handling."},
        {"type": "tool_call", "tool": "run_tests", "arguments": {"path": "tests/"}, "output": "All tests passed! ✓\n" * 50},
        {"type": "assistant_message", "content": "Done! The code has been refactored with error handling."},
    ]


def test_compactor(compactor, name: str) -> bool:
    """Test a single compactor for reversibility."""
    context = create_test_context()
    original_tokens = sum(len(json.dumps(e, sort_keys=True)) for e in context)
    
    print(f"\nTesting {name}...")
    print(f"  Original: {len(context)} entries, ~{original_tokens} chars")
    
    # Compact
    result = compactor.compact(context)
    
    print(f"  Compacted: {result.entries_preserved} preserved, {result.entries_compacted} offloaded")
    print(f"  Tokens saved: ~{result.tokens_saved}")
    
    # Save offloaded data to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(result.offloaded_data, f)
        offload_path = f.name
    
    try:
        # Restore
        restored = compactor.restore(result.compacted_context, offload_path)
        
        # Verify
        original_serialized = [json.dumps(e, sort_keys=True) for e in context]
        restored_serialized = [json.dumps(e, sort_keys=True) for e in restored]
        
        if original_serialized == restored_serialized:
            print("  ✓ RESTORE SUCCESSFUL - Perfect reversibility")
            return True
        else:
            print("  ✗ RESTORE FAILED - Data mismatch")
            # Find differences
            for i, (orig, rest) in enumerate(zip(original_serialized, restored_serialized)):
                if orig != rest:
                    print(f"    Difference at index {i}")
                    print(f"      Original: {orig[:100]}...")
                    print(f"      Restored: {rest[:100]}...")
            return False
    finally:
        os.unlink(offload_path)


def test_all_strategies():
    """Test all compaction strategies."""
    config = CompactionConfig(
        strategy=CompactionStrategy.HYBRID,
        keep_recent_full=3,
        compact_ratio=0.4,
    )
    
    strategies = [
        (TokenBudgetCompactor(config), "TokenBudgetCompactor"),
        (AgeBasedCompactor(config), "AgeBasedCompactor"),
        (ImportanceBasedCompactor(config), "ImportanceBasedCompactor"),
        (HybridCompactor(config), "HybridCompactor"),
        (TimestampHidingCompactor(config), "TimestampHidingCompactor"),
        (HeadTailProtectionCompactor(config), "HeadTailProtectionCompactor"),
        (RepeatedToolPruningCompactor(config), "RepeatedToolPruningCompactor"),
        (ErrorPreservationCompactor(config), "ErrorPreservationCompactor"),
    ]
    
    results = {}
    for compactor, name in strategies:
        try:
            results[name] = test_compactor(compactor, name)
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results[name] = False
    
    print("\n" + "="*50)
    print("SUMMARY:")
    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        print(f"  {name}: {status}")
    
    all_passed = all(results.values())
    print(f"\nOverall: {'ALL TESTS PASSED ✓' if all_passed else 'SOME TESTS FAILED ✗'}")
    return all_passed


def test_main_compactor():
    """Test the main Compactor factory."""
    print("\n" + "="*50)
    print("Testing Main Compactor Factory...")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({
            "thresholds": {"hard_limit": 200000, "pre_rot_threshold": 100000, "compaction_trigger": 150000, "summarization_trigger": 175000},
            "compaction": {"strategy": "hybrid", "keep_recent_full": 3, "compact_ratio": 0.4},
            "summarization": {"schema": "agent_default", "keep_recent_full": 3, "model": "opencode/big-pickle"},
            "offloading": {"base_path": ".agent_context", "compression": "gzip", "index_format": "jsonl"},
            "kv_cache": {"enforce_stable_prefix": True, "append_only": True, "deterministic_json": True},
        }, f)
        config_path = f.name
    
    try:
        compactor = Compactor.from_config(config_path)
        context = create_test_context()
        result = compactor.compact(context)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(result.offloaded_data, f)
            offload_path = f.name
        
        restored = compactor.restore(result.compacted_context, offload_path)
        
        original_serialized = [json.dumps(e, sort_keys=True) for e in context]
        restored_serialized = [json.dumps(e, sort_keys=True) for e in restored]
        
        if original_serialized == restored_serialized:
            print("  ✓ Main Compactor Factory - Perfect reversibility")
            return True
        else:
            print("  ✗ Main Compactor Factory - Data mismatch")
            return False
    finally:
        os.unlink(config_path)
        os.unlink(offload_path)


if __name__ == "__main__":
    print("="*60)
    print("COMPACTION REVERSIBILITY TESTS")
    print("="*60)
    
    all_passed = test_all_strategies()
    all_passed = test_main_compactor() and all_passed
    
    if all_passed:
        print("\n✓ ALL COMPACTION TESTS PASSED")
        exit(0)
    else:
        print("\n✗ SOME COMPACTION TESTS FAILED")
        exit(1)
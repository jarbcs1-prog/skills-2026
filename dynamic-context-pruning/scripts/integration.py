"""
Integration — Agent loop integration helpers for dynamic context pruning.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

from context_monitor import ContextMonitor, ContextAction
from compaction import Compactor
from summarization import Summarizer, SCHEMAS
from file_offloader import FileOffloader
from platform import detect_platform, Platform


def create_components(config_path: str = ".agent_context_config.json", platform: Optional[Platform] = None) -> Tuple[ContextMonitor, Compactor, Summarizer, FileOffloader, Platform]:
    """
    Create all context pruning components with platform-specific configuration.
    
    Returns:
        (monitor, compactor, summarizer, offloader, platform)
    """
    if platform is None:
        platform = detect_platform()
    
    # Load config with platform-specific defaults
    with open(config_path) as f:
        user_config = json.load(f)
    
    # Apply platform-specific config merging
    from platform import merge_config_with_platform
    
    merged_config = merge_config_with_platform(user_config, detect_platform())
    
    # Write merged config to temp file for component initialization
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(merged_config, f)
        temp_config_path = f.name
    
    try:
        monitor = ContextMonitor.from_config(temp_config_path)
        compactor = Compactor.from_config(temp_config_path)
        summarizer = Summarizer.from_config(temp_config_path, platform.value)
        offloader = FileOffloader.from_config(temp_config_path)
    finally:
        Path(temp_config_path).unlink(missing_ok=True)
    
    return monitor, compactor, summarizer, offloader, detect_platform()


async def agent_step(
    context_history: List[Dict[str, Any]],
    config_path: str = ".agent_context_config.json",
    platform: Optional[Platform] = None,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Process a single agent step with context pruning.
    
    Returns:
        (updated_context_history, step_metadata)
    """
    monitor, compactor, summarizer, offloader, platform = create_components(config_path)
    
    # Estimate current tokens
    from token_estimator import estimate_context_tokens
    current_tokens = estimate_context_tokens(context_history)
    
    # Check context health
    status = monitor.check_context(current_tokens)
    
    step_metadata = {
        "tokens_before": current_tokens,
        "action": status.action.value,
        "percent": status.percent,
        "message": status.message,
    }
    
    if status.action == ContextAction.COMPACT:
        # Compact oldest context
        compacted, offloaded = compactor.compact(context_history)
        
        # Offload to filesystem
        ref = offloader.offload(
            offloaded,
            metadata={"phase": "compaction", "platform": platform.value}
        )
        
        # Replace with compacted + reference
        context_history = compacted + [{
            "type": "context_reference",
            "ref": {
                "path": ref.path,
                "url": ref.url,
                "tokens": ref.tokens,
                "sha256": ref.sha256,
            }
        }]
        
        step_metadata.update({
            "entries_compacted": len(offloaded),
            "entries_preserved": len(compacted),
            "tokens_saved": sum(len(json.dumps(e)) // 4 for e in offloaded),
            "offload_path": ref.path,
        })
        
    elif status.action == ContextAction.SUMMARIZE:
        # Summarize with structured schema
        summary = summarizer.summarize(context_history[:-3])  # Keep last 3
        
        # Offload full context for recovery
        ref = offloader.offload(
            context_history[:-3],
            metadata={"phase": "summarization", "platform": platform.value}
        )
        
        # Replace with summary + reference
        context_history = [{
            "type": "summary",
            "data": summary.summary,
            "schema": summary.schema_used,
        }, {
            "type": "context_reference",
            "ref": {
                "path": ref.path,
                "url": ref.url,
                "tokens": ref.tokens,
                "sha256": ref.sha256,
            }
        }] + context_history[-3:]
        
        step_metadata.update({
            "entries_summarized": summary.entries_summarized,
            "entries_preserved": summary.entries_preserved,
            "summary_tokens": summary.tokens_estimated,
            "offload_path": ref.path,
        })
    
    elif status.action == ContextAction.CRITICAL:
        step_metadata["critical"] = True
        step_metadata["message"] = "Context exceeded hard limit - immediate action required"
    
    # Recalculate tokens after pruning
    from token_estimator import estimate_context_tokens
    step_metadata["tokens_after"] = estimate_context_tokens(context_history)
    
    return context_history, step_metadata


def restore_context(
    context_history: List[Dict[str, Any]],
    config_path: str = ".agent_context_config.json",
) -> List[Dict[str, Any]]:
    """Restore full context from references in history."""
    offloader = FileOffloader.from_config(config_path)
    restored = []
    
    for entry in context_history:
        if entry.get("type") == "context_reference" and "ref" in entry:
            ref_data = entry["ref"]
            restored_data = offloader.restore(ref_data["path"])
            restored.extend(restored_data)
        elif entry.get("type") == "summary":
            # Summaries can't be fully restored, keep as-is
            restored.append(entry)
        else:
            restored.append(entry)
    
    return restored


def get_context_health(context_history: List[Dict[str, Any]], config_path: str = ".agent_context_config.json") -> Dict[str, Any]:
    """Get comprehensive context health report."""
    from token_estimator import estimate_context_tokens, calculate_context_utilization
    
    monitor = ContextMonitor.from_config(config_path)
    current_tokens = estimate_context_tokens(context_history)
    status = monitor.check_context(current_tokens)
    metrics = monitor.get_metrics()
    
    return {
        "tokens": current_tokens,
        "percent": status.percent,
        "action": status.action.value,
        "message": status.message,
        "metrics": {
            "trend": metrics.trend,
            "predicted_exhaustion": metrics.predicted_exhaustion,
            "time_to_compaction": metrics.time_to_compaction,
            "time_to_summarization": metrics.time_to_summarization,
        },
        "history_length": len(context_history),
        "utilization": calculate_context_utilization(context_history),
    }


def create_config_for_platform(
    platform: Platform,
    output_path: str = ".agent_context_config.json",
) -> None:
    """Create platform-specific configuration file."""
    from platform import get_platform_config_defaults
    
    defaults = get_platform_config_defaults(platform)
    defaults["platform"] = platform.value
    
    with open(output_path, "w") as f:
        json.dump(defaults, f, indent=2)
    
    print(f"Created {output_path} for {platform.value} platform")


def validate_config(config_path: str = ".agent_context_config.json") -> List[str]:
    """Validate configuration file. Returns list of errors."""
    errors = []
    
    try:
        with open(config_path) as f:
            config = json.load(f)
    except FileNotFoundError:
        return [f"Config file not found: {config_path}"]
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]
    
    # Validate thresholds
    thresholds = config.get("thresholds", {})
    required_thresholds = ["hard_limit", "pre_rot_threshold", "compaction_trigger", "summarization_trigger"]
    for key in required_thresholds:
        if key not in thresholds:
            errors.append(f"Missing threshold: {key}")
    
    # Check threshold ordering
    if all(k in thresholds for k in required_thresholds):
        if not (thresholds["pre_rot_threshold"] < thresholds["compaction_trigger"] < 
                thresholds["summarization_trigger"] < thresholds["hard_limit"]):
            errors.append("Thresholds must be ordered: pre_rot < compaction < summarization < hard_limit")
    
    # Validate compaction
    compaction = config.get("compaction", {})
    if "strategy" in compaction:
        valid_strategies = [
            "token_budget", "age_based", "importance_based", "hybrid",
            "timestamp_hiding", "head_tail_protection", "repeated_tool_pruning", "error_preservation"
        ]
        if compaction["strategy"] not in valid_strategies:
            errors.append(f"Invalid compaction strategy: {compaction['strategy']}")
    
    # Validate summarization
    summ = config.get("summarization", {})
    if "schema" in summ:
        valid_schemas = list(SCHEMAS.keys()) + ["auto"]
        if summ["schema"] not in valid_schemas:
            errors.append(f"Invalid summarization schema: {summ['schema']}")
    
    return errors


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Integration CLI")
    parser.add_argument("--config", default=".agent_context_config.json")
    parser.add_argument("--platform", choices=["generic", "opencode", "auto"], default="auto")
    parser.add_argument("--create-config", action="store_true", help="Create config for platform")
    parser.add_argument("--validate", action="store_true", help="Validate config")
    parser.add_argument("--health", action="store_true", help="Check context health")
    parser.add_argument("--context", help="Context JSON file for health check")
    args = parser.parse_args()

    if args.create_config:
        platform = Platform(args.platform) if args.platform != "auto" else detect_platform()
        create_config_for_platform(platform, args.config)
    elif args.validate:
        errors = validate_config(args.config)
        if errors:
            print("Config validation FAILED:")
            for e in errors:
                print(f"  - {e}")
        else:
            print("Config validation PASSED ✓")
    elif args.health:
        if not args.context:
            parser.error("--context required for health check")
        with open(args.context) as f:
            context = json.load(f)
        health = get_context_health(context, args.config)
        print(json.dumps(health, indent=2, default=str))
    else:
        parser.error("One of --create-config, --validate, --health required")


if __name__ == "__main__":
    main()
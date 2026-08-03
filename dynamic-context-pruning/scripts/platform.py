"""
Platform Detection — Auto-detect agent platform (Generic vs OpenCode).
"""

import os
import json
from enum import Enum
from pathlib import Path
from dataclasses import dataclass


class Platform(Enum):
    GENERIC = "generic"
    OPENCODE = "opencode"
    AUTO = "auto"


@dataclass
class PlatformInfo:
    platform: Platform
    confidence: float
    indicators: dict


def detect_platform() -> Platform:
    """
    Detect the current agent platform.
    
    Returns:
        Platform.GENERIC, Platform.OPENCODE, or Platform.AUTO
    """
    # Check OpenCode-specific environment variables
    if os.environ.get("OPENCODE_SESSION_ID"):
        return Platform.OPENCODE
    
    if os.environ.get("AGENT_FRAMEWORK") == "opencode":
        return Platform.OPENCODE
    
    # Check for .opencode directory
    if Path(".opencode").exists():
        return Platform.OPENCODE
    
    # Check for opencode config files
    if Path(".opencode_context_config.json").exists():
        return Platform.OPENCODE
    
    # Check for opencode in workspace
    if Path("opencode.toml").exists() or Path("opencode.json").exists():
        return Platform.OPENCODE
    
    return Platform.GENERIC


def get_platform_info() -> PlatformInfo:
    """Get detailed platform detection info."""
    indicators = {
        "OPENCODE_SESSION_ID": bool(os.environ.get("OPENCODE_SESSION_ID")),
        "AGENT_FRAMEWORK": os.environ.get("AGENT_FRAMEWORK") == "opencode",
        "opencode_dir": Path(".opencode").exists(),
        "opencode_config": Path(".opencode_context_config.json").exists(),
        "opencode_toml": Path("opencode.toml").exists(),
        "opencode_json": Path("opencode.json").exists(),
    }
    
    opencode_score = sum(indicators.values())
    
    if opencode_score > 0:
        return PlatformInfo(
            platform=Platform.OPENCODE,
            confidence=min(0.9, 0.5 + opencode_score * 0.1),
            indicators=indicators,
        )
    
    return PlatformInfo(
        platform=Platform.GENERIC,
        confidence=0.7,
        indicators=indicators,
    )


def get_platform_config_defaults(platform: Platform) -> dict:
    """Get platform-specific configuration defaults."""
    if platform == Platform.OPENCODE:
        return {
            "thresholds": {
                "hard_limit": 200_000,
                "pre_rot_threshold": 100_000,
                "compaction_trigger": 150_000,
                "summarization_trigger": 175_000,
            },
            "compaction": {
                "strategy": "timestamp_hiding",
                "keep_recent_full": 5,
                "protect_zones": ["head", "tail"],
                "max_tool_output_tokens": 2000,
            },
            "summarization": {
                "schema": "opencode_5_heading",
                "keep_recent_full": 3,
                "model": "opencode/big-pickle",
            },
            "offloading": {
                "base_path": ".opencode_context",
                "compression": "gzip",
                "index_format": "jsonl",
            },
        }
    else:
        return {
            "thresholds": {
                "hard_limit": 256_000,
                "pre_rot_threshold": 100_000,
                "compaction_trigger": 150_000,
                "summarization_trigger": 175_000,
            },
            "compaction": {
                "strategy": "hybrid",
                "keep_recent_full": 5,
                "compact_ratio": 0.5,
            },
            "summarization": {
                "schema": "agent_default",
                "keep_recent_full": 3,
                "model": "opencode/big-pickle",
            },
            "offloading": {
                "base_path": ".agent_context",
                "compression": "gzip",
                "index_format": "jsonl",
            },
        }


def merge_config_with_platform(config: dict, platform: Platform) -> dict:
    """Merge user config with platform defaults."""
    defaults = get_platform_config_defaults(platform)
    
    def deep_merge(base: dict, override: dict) -> dict:
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    return deep_merge(defaults, config)


def get_schema_for_platform(platform: Platform) -> str:
    """Get summarization schema for platform."""
    if platform == Platform.OPENCODE:
        return "opencode_5_heading"
    return "agent_default"


def get_compaction_strategy_for_platform(platform: Platform) -> str:
    """Get compaction strategy for platform."""
    if platform == Platform.OPENCODE:
        return "timestamp_hiding"
    return "hybrid"


def get_offload_base_path(platform: Platform) -> str:
    """Get offloading base path for platform."""
    if platform == Platform.OPENCODE:
        return ".opencode_context"
    return ".agent_context"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Platform Detection CLI")
    parser.add_argument("--detect", action="store_true", help="Detect and print platform")
    parser.add_argument("--info", action="store_true", help="Show detailed detection info")
    parser.add_argument("--defaults", action="store_true", help="Show platform defaults")
    args = parser.parse_args()

    if args.detect:
        platform = detect_platform()
        print(platform.value)
    elif args.info:
        info = get_platform_info()
        print(f"Platform: {info.platform.value}")
        print(f"Confidence: {info.confidence:.2f}")
        print("Indicators:")
        for k, v in info.indicators.items():
            print(f"  {k}: {v}")
    elif args.defaults:
        platform = detect_platform()
        defaults = get_platform_config_defaults(platform)
        print(json.dumps(defaults, indent=2))
    else:
        parser.error("One of --detect, --info, --defaults required")


if __name__ == "__main__":
    main()
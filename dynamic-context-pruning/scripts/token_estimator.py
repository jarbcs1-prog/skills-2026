"""
Token Estimator — Token estimation using tiktoken for various models.
"""

import json
from typing import List, Dict, Any

# Try to import tiktoken, fall back to rough estimation if not available
try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


# Model to encoding mapping
MODEL_ENCODINGS = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "o200k_base",
    "gpt-4o-mini": "o200k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "claude-3": "cl100k_base",  # Approximation
    "claude-sonnet-4": "cl100k_base",  # Approximation
    "opencode/big-pickle": "cl100k_base",  # Approximation
    "nemotron-3-ultra": "cl100k_base",  # Approximation
}


def get_encoding_for_model(model: str):
    """Get tiktoken encoding for a model."""
    if not TIKTOKEN_AVAILABLE:
        return None
    
    encoding_name = MODEL_ENCODINGS.get(model, "cl100k_base")
    try:
        return tiktoken.get_encoding(encoding_name)
    except Exception:
        return tiktoken.get_encoding("cl100k_base")


def estimate_tokens(text: str, model: str = "gpt-4") -> int:
    """Estimate token count for text using tiktoken or fallback."""
    if TIKTOKEN_AVAILABLE:
        encoding = get_encoding_for_model(model)
        if encoding:
            return len(encoding.encode(text))
    
    # Fallback: rough estimation (4 chars ≈ 1 token for English)
    return len(text) // 4


def estimate_context_tokens(context: List[Dict[str, Any]], model: str = "gpt-4") -> int:
    """Estimate total tokens for a context history."""
    total = 0
    for entry in context:
        # Serialize entry deterministically
        serialized = json.dumps(entry, sort_keys=True)
        total += estimate_tokens(serialized, model)
    return total


def estimate_entry_tokens(entry: Dict[str, Any], model: str = "gpt-4") -> int:
    """Estimate tokens for a single context entry."""
    serialized = json.dumps(entry, sort_keys=True)
    return estimate_tokens(serialized, model)


def get_model_context_window(model: str) -> int:
    """Get context window size for a model."""
    windows = {
        "gpt-4": 8192,
        "gpt-4o": 128000,
        "gpt-4o-mini": 128000,
        "gpt-3.5-turbo": 16384,
        "claude-3": 200000,
        "claude-sonnet-4": 200000,
        "opencode/big-pickle": 200000,
        "nemotron-3-ultra": 128000,
    }
    return windows.get(model, 8192)


def calculate_context_utilization(context: List[Dict[str, Any]], model: str = "gpt-4") -> float:
    """Calculate context utilization as percentage of model window."""
    tokens = estimate_context_tokens(context, model)
    window = get_model_context_window(model)
    return (tokens / window) * 100


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Token Estimator CLI")
    parser.add_argument("--input", help="Input context JSON file")
    parser.add_argument("--model", default="gpt-4", help="Model name for estimation")
    parser.add_argument("--text", help="Direct text to estimate")
    args = parser.parse_args()

    if args.text:
        tokens = estimate_tokens(args.text, args.model)
        print(f"Estimated tokens: {tokens}")
    elif args.input:
        with open(args.input) as f:
            context = json.load(f)
        tokens = estimate_context_tokens(context, args.model)
        window = get_model_context_window(args.model)
        utilization = (tokens / window) * 100
        print(f"Context tokens: {tokens}")
        print(f"Model window: {window}")
        print(f"Utilization: {utilization:.1f}%")
    else:
        parser.error("Either --input or --text required")


if __name__ == "__main__":
    main()
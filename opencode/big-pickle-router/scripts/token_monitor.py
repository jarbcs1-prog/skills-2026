import json
import os
import argparse

LIMIT = int(os.environ.get("DAILY_TOKEN_LIMIT", "1300"))
USAGE_FILE = "daily_usage.json"

def check_and_delegate(current_request_tokens):
    """
    Tracks token usage and returns True if the daily limit is reached.
    """
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE, 'r') as f:
            try:
                usage = json.load(f)
            except json.JSONDecodeError:
                usage = {"total_tokens": 0}
    else:
        usage = {"total_tokens": 0}

    usage["total_tokens"] += current_request_tokens
    
    with open(USAGE_FILE, 'w') as f:
        json.dump(usage, f, indent=2)

    if usage["total_tokens"] >= LIMIT:
        print(f"DAILY LIMIT REACHED: {usage['total_tokens']}/{LIMIT} tokens.")
        return True
    
    print(f"Token Usage: {usage['total_tokens']}/{LIMIT}")
    return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track daily token usage")
    parser.add_argument("tokens", nargs="?", type=int, help="Tokens used in last call")
    parser.add_argument("--limit", type=int, default=None, help="Override daily token limit")
    args = parser.parse_args()

    if args.limit is not None:
        LIMIT = args.limit

    if args.tokens is not None:
        reached = check_and_delegate(args.tokens)
        if reached:
            print("Action: Triggering Zen-Delegator...")
    else:
        print("Usage: python token_monitor.py <tokens_used_in_last_call> [--limit N]")

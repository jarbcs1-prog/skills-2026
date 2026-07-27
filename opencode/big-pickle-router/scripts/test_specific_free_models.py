"""Standalone API test — verify Zen models are reachable.

Run directly: python scripts/test_specific_free_models.py
Requires: OPENCODE_API_KEY environment variable.
"""

import requests
import os
import sys


def check_models(model_list):
    api_key = os.environ.get("OPENCODE_API_KEY", "")
    if not api_key:
        print("ERROR: OPENCODE_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    url = "https://opencode.ai/zen/v1/chat/completions"

    for model in model_list:
        print(f"--- Testing {model} ---")
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Say 'Active'"}],
            "max_tokens": 10
        }
        try:
            response = requests.post(url, headers=headers, json=data)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text}")
        except Exception as e:
            print(f"Error: {e}")
        print()


if __name__ == "__main__":
    requested_models = [
        "opencode/big-pickle",
        "opencode/north-mini-code-free",
        "opencode/nemotron-3-ultra-free",
        "opencode/deepseek-v4-flash-free",
        "opencode/mimo-v2.5-free",
        "opencode/ling-3.0-flash-free",
        "opencode/laguna-s-2.1-free"
    ]
    check_models(requested_models)

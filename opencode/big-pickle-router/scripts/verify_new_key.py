import requests
import os
import argparse

def get_api_key(cli_key=None):
    if cli_key:
        return cli_key
    return os.environ.get("OPENCODE_API_KEY", "")

def test_endpoint(name, url, model, api_key, payload_type="openai"):
    print(f"--- Testing {name} ({model}) ---")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    if payload_type == "anthropic":
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Say hello!"}],
            "max_tokens": 20
        }
    else:
        data = {
            "model": model,
            "messages": [{"role": "user", "content": "Say hello!"}],
            "max_tokens": 20
        }

    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")
    print()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test API key against OpenCode Zen endpoints")
    parser.add_argument("--key", type=str, default=None, help="API key (or set OPENCODE_API_KEY env var)")
    args = parser.parse_args()

    api_key = get_api_key(args.key)
    if not api_key:
        print("Error: No API key. Set OPENCODE_API_KEY or pass --key")
        exit(1)

    test_endpoint("Big Pickle", "https://opencode.ai/zen/v1/chat/completions", "opencode/big-pickle", api_key)
    test_endpoint("Claude Fable 5", "https://opencode.ai/zen/v1/messages", "claude-fable-5", api_key, payload_type="anthropic")
    test_endpoint("Qwen3 Coder", "https://opencode.ai/zen/v1/chat/completions", "qwen3-coder", api_key)

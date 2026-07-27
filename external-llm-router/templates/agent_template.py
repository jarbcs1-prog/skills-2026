#!/usr/bin/env python3
"""Template: Custom LLM provider agent using external-llm-router patterns."""

import argparse
import json
import os
import sys

import requests


def send_prompt(url: str, model: str, prompt: str, api_key: str,
                context_path: str | None = None, system: str | None = None,
                max_tokens: int = 4096) -> dict:
    """Send a prompt to an LLM endpoint and return the response."""
    headers = {"Content-Type": "application/json"}

    if "anthropic.com" in url:
        headers["x-api-key"] = api_key
        headers["anthropic-version"] = "2023-06-01"
        messages = [{"role": "user", "content": prompt}]
        if context_path and os.path.exists(context_path):
            with open(context_path) as f:
                messages = json.load(f) + messages
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
        }
        if system:
            payload["system"] = system
    else:
        headers["Authorization"] = f"Bearer {api_key}"
        messages = [{"role": "user", "content": prompt}]
        if context_path and os.path.exists(context_path):
            with open(context_path) as f:
                messages = json.load(f) + messages
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
        }

    resp = requests.post(url, headers=headers, json=payload, timeout=120)
    resp.raise_for_status()
    return resp.json()


def main():
    parser = argparse.ArgumentParser(description="Custom LLM agent template")
    parser.add_argument("--url", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--prompt", required=True)
    parser.add_argument("--api-key", default=os.environ.get("LLM_API_KEY", ""))
    parser.add_argument("--context", default=None)
    parser.add_argument("--system", default=None)
    parser.add_argument("--max-tokens", type=int, default=4096)
    args = parser.parse_args()

    if not args.api_key:
        print("Error: No API key. Set LLM_API_KEY env var or pass --api-key", file=sys.stderr)
        sys.exit(1)

    result = send_prompt(
        args.url, args.model, args.prompt, args.api_key,
        args.context, args.system, args.max_tokens,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

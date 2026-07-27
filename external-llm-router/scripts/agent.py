"""External LLM Router — Agent client.

Sends prompts to OpenAI-compatible or Anthropic endpoints with retry logic,
environment-based API key resolution, and reasoning_content support.

Usage:
    python agent.py --url URL --model MODEL --prompt "Hello"
    python agent.py --url URL --model MODEL --prompt "Continue" --context ctx.json
    python agent.py --url URL --model MODEL --prompt "Hello" --reset-usage daily_usage.json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

MAX_RETRIES = 3
BACKOFF_BASE = 1.0  # seconds; doubles each retry


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def _load_dotenv(search_dir: Path | None = None) -> None:
    """Best-effort .env loader — no third-party deps."""
    if search_dir is None:
        search_dir = Path.cwd()
    env_file = search_dir / ".env"
    if not env_file.is_file():
        return
    with open(env_file, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = value


def resolve_api_key(explicit: str | None, env_var: str) -> str:
    """Return the explicit key, then the env var, or raise."""
    if explicit:
        return explicit
    val = os.environ.get(env_var)
    if val:
        return val
    raise SystemExit(
        f"Error: No API key provided. Set {env_var} in the environment "
        f"or pass --api-key."
    )


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

def _is_retryable(status: int) -> bool:
    return status == 429 or status >= 500


def _request_with_retry(
    method: str,
    url: str,
    *,
    headers: dict[str, str],
    json_data: dict[str, Any] | None = None,
    max_retries: int = MAX_RETRIES,
) -> requests.Response:
    """Perform an HTTP request with exponential backoff on 429/5xx."""
    last_exc: Exception | None = None
    for attempt in range(max_retries):
        try:
            resp = requests.request(
                method, url, headers=headers, json=json_data, timeout=120
            )
            if _is_retryable(resp.status_code) and attempt < max_retries - 1:
                wait = BACKOFF_BASE * (2 ** attempt)
                retry_after = resp.headers.get("Retry-After")
                if retry_after:
                    try:
                        wait = max(wait, float(retry_after))
                    except ValueError:
                        pass
                print(
                    f"[retry] {resp.status_code} — waiting {wait:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            return resp
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_exc = exc
            if attempt < max_retries - 1:
                wait = BACKOFF_BASE * (2 ** attempt)
                print(
                    f"[retry] {exc} — waiting {wait:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries})",
                    file=sys.stderr,
                )
                time.sleep(wait)
                continue
            raise
    raise last_exc  # type: ignore[misc]


# ---------------------------------------------------------------------------
# Endpoint detection
# ---------------------------------------------------------------------------

def _detect_provider(url: str) -> str:
    """Return 'anthropic' or 'openai' based on the URL path."""
    lower = url.lower()
    if "/v1/messages" in lower or "api.anthropic.com" in lower:
        return "anthropic"
    return "openai"


# ---------------------------------------------------------------------------
# Core API
# ---------------------------------------------------------------------------

def call_model(
    api_key: str,
    url: str,
    model: str,
    prompt: str,
    context: list[dict[str, str]] | None = None,
    *,
    system: str | None = None,
    max_tokens: int = 4096,
) -> dict[str, Any]:
    """Send a prompt to an LLM endpoint and return a structured result.

    Supports both OpenAI-compatible chat/completions and Anthropic messages
    endpoints.  The provider is auto-detected from *url*.

    Returns:
        ``{"success": True, "content": str, "reasoning": str}`` on success,
        or ``{"success": False, "error": str}`` on failure.
    """
    provider = _detect_provider(url)
    messages: list[dict[str, str]] = list(context or [])
    messages.append({"role": "user", "content": prompt})

    if provider == "anthropic":
        return _call_anthropic(api_key, url, model, messages, system, max_tokens)
    return _call_openai(api_key, url, model, messages, max_tokens)


def _call_openai(
    api_key: str,
    url: str,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    data: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "stream": False,
    }
    resp = _request_with_retry("POST", url, headers=headers, json_data=data)
    if resp.status_code != 200:
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
    result = resp.json()
    message = result["choices"][0]["message"]
    return {
        "success": True,
        "content": message.get("content", ""),
        "reasoning": message.get("reasoning_content", ""),
    }


def _call_anthropic(
    api_key: str,
    url: str,
    model: str,
    messages: list[dict[str, str]],
    system: str | None,
    max_tokens: int,
) -> dict[str, Any]:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "Content-Type": "application/json",
    }
    data: dict[str, Any] = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
    }
    if system:
        data["system"] = system
    resp = _request_with_retry("POST", url, headers=headers, json_data=data)
    if resp.status_code != 200:
        return {"success": False, "error": f"HTTP {resp.status_code}: {resp.text}"}
    result = resp.json()
    text = "".join(
        block.get("text", "") for block in result.get("content", [])
    )
    return {"success": True, "content": text, "reasoning": ""}


# ---------------------------------------------------------------------------
# Usage reset helper
# ---------------------------------------------------------------------------

def reset_usage_file(path: str) -> None:
    """Truncate the monitor usage file so the counter starts fresh."""
    p = Path(path)
    p.write_text(json.dumps({"total": 0, "date": ""}, indent=2) + "\n")
    print(f"Usage file reset: {p}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Send a prompt to an external LLM via OpenAI or Anthropic API.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--url", required=True, help="Chat/completions or messages endpoint URL")
    p.add_argument("--model", required=True, help="Model identifier (e.g. opencode/big-pickle)")
    p.add_argument("--prompt", required=True, help="User prompt text")
    p.add_argument("--api-key", default=None, help="API key (falls back to env var)")
    p.add_argument("--env-var", default="OPENCODE_API_KEY", help="Env var name for the API key (default: OPENCODE_API_KEY)")
    p.add_argument("--context", default=None, help="Path to JSON file with prior conversation messages")
    p.add_argument("--system", default=None, help="System prompt (Anthropic endpoints only)")
    p.add_argument("--max-tokens", type=int, default=4096, help="Max tokens in response (default: 4096)")
    p.add_argument("--reset-usage", default=None, metavar="FILE", help="Reset the given usage tracking file before sending")
    return p


def main(argv: list[str] | None = None) -> None:
    """CLI entry point."""
    _load_dotenv()
    args = _build_parser().parse_args(argv)

    if args.reset_usage:
        reset_usage_file(args.reset_usage)

    api_key = resolve_api_key(args.api_key, args.env_var)

    context: list[dict[str, str]] | None = None
    if args.context:
        path = Path(args.context)
        if not path.is_file():
            raise SystemExit(f"Context file not found: {path}")
        with open(path, encoding="utf-8") as fh:
            context = json.load(fh)

    result = call_model(
        api_key,
        args.url,
        args.model,
        args.prompt,
        context=context,
        system=args.system,
        max_tokens=args.max_tokens,
    )

    if result["success"]:
        if result["reasoning"]:
            print(f"--- REASONING ---\n{result['reasoning']}\n")
        print(f"--- RESPONSE ---\n{result['content']}")
    else:
        print(f"Error: {result['error']}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

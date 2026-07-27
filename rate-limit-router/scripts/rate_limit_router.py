import argparse
import json
import os
import sys
import time
import requests


def load_config(config_path=None):
    """Load config from file path, RATE_LIMIT_CONFIG env var, or ./config.json."""
    if config_path is None:
        config_path = os.environ.get("RATE_LIMIT_CONFIG", "./config.json")

    if not os.path.exists(config_path):
        json.dump({"error": f"Config file not found: {config_path}"}, sys.stderr)
        print(file=sys.stderr)
        sys.exit(1)

    with open(config_path, 'r') as f:
        return json.load(f)


def detect_provider(model_id):
    """Detect API provider from model ID format.
    Contains ':' → OpenRouter, no ':' → Zen.
    """
    if ':' in model_id:
        return "openrouter"
    return "zen"


def get_fallback(model_id, config):
    """Look up fallback model for the given model ID.
    Returns the alternate provider's model ID, or None if no mapping exists.
    """
    provider = detect_provider(model_id)
    if provider == "zen":
        return config.get("fallback_map", {}).get(model_id)
    else:
        return config.get("reverse_map", {}).get(model_id)


def backoff_sleep(attempt, config):
    """Calculate and return the backoff delay for the given attempt.
    Does NOT sleep — returns the delay value for testability.
    """
    backoff = config.get("backoff", {})
    initial = backoff.get("initial_delay", 1)
    multiplier = backoff.get("multiplier", 2)
    max_delay = backoff.get("max_delay", 16)
    delay = initial * (multiplier ** attempt)
    return min(delay, max_delay)


def get_api_key(provider):
    """Get API key from environment variable. Raises ValueError if missing."""
    env_var = "ZEN_API_KEY" if provider == "zen" else "OPENROUTER_API_KEY"
    key = os.environ.get(env_var, "")
    if not key:
        raise ValueError(f"Missing {env_var} environment variable")
    return key


def call_api(provider, model, messages, config, stream=True):
    """Make an API call to the specified provider with retry + exponential backoff.
    Returns: {"success": bool, "content": str, "status": int, "error": str, "attempts": int}
    """
    provider_config = config.get(provider, {})
    base_url = provider_config.get("base_url")
    api_key = get_api_key(provider)
    max_retries = config.get("backoff", {}).get("max_retries", 3)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    if provider == "openrouter":
        headers["HTTP-Referer"] = "https://opencode.ai"
        headers["X-Title"] = "Rate Limit Router"

    data = {
        "model": model,
        "messages": messages,
        "stream": stream
    }

    last_error = None
    for attempt in range(max_retries + 1):
        try:
            response = requests.post(base_url, headers=headers, json=data, timeout=60)

            if response.status_code == 200:
                if stream:
                    return {"success": True, "status": 200, "stream_response": response, "attempts": attempt + 1}
                else:
                    result = response.json()
                    content = result['choices'][0]['message'].get('content', '')
                    reasoning = result['choices'][0]['message'].get('reasoning_content', '')
                    return {"success": True, "content": content, "reasoning": reasoning, "status": 200, "attempts": attempt + 1}

            # Non-retryable: auth/forbidden errors → break immediately
            if response.status_code in (401, 403):
                return {"success": False, "status": response.status_code, "error": response.text, "attempts": attempt + 1}

            # Retryable: 429, 5xx
            if response.status_code == 429 or response.status_code >= 500:
                last_error = response.text
                last_status = response.status_code
                if attempt < max_retries:
                    delay = backoff_sleep(attempt, config)
                    time.sleep(delay)
                    continue
                return {"success": False, "status": last_status, "error": last_error, "attempts": attempt + 1}

            # Other status codes: non-retryable
            return {"success": False, "status": response.status_code, "error": response.text, "attempts": attempt + 1}

        except requests.exceptions.RequestException as e:
            last_error = str(e)
            last_status = 0
            if attempt < max_retries:
                delay = backoff_sleep(attempt, config)
                time.sleep(delay)
                continue
            return {"success": False, "status": last_status, "error": last_error, "attempts": attempt + 1}

    return {"success": False, "status": last_status, "error": last_error, "attempts": max_retries + 1}


def route(model, messages, config, stream=True, verbose=False):
    """Route an API call with automatic fallback on rate limits.
    Returns: {"success": bool, "content": str, "provider": str, "fallback": bool, "attempts": list}
    """
    provider = detect_provider(model)
    fallback_model = get_fallback(model, config)
    max_retries = config.get("backoff", {}).get("max_retries", 3)

    attempts = []

    if verbose:
        print(f"[{provider.title()}] Trying {model}...", file=sys.stderr)

    result = call_api(provider, model, messages, config, stream=stream)
    attempts.append({"provider": provider, "model": model, "status": result.get("status")})

    if result["success"]:
        result["provider"] = provider
        result["fallback"] = False
        result["attempts"] = attempts
        return result

    if result["status"] in (401, 403):
        result["provider"] = provider
        result["fallback"] = False
        result["attempts"] = attempts
        return result

    if fallback_model is None:
        result["provider"] = provider
        result["fallback"] = False
        result["attempts"] = attempts
        return result

    fallback_provider = detect_provider(fallback_model)
    if verbose:
        print(f"[Retry] 429 from {provider}, trying {fallback_provider}: {fallback_model}", file=sys.stderr)

    for attempt in range(max_retries):
        delay = backoff_sleep(attempt, config)
        if verbose:
            print(f"[Backoff] Waiting {delay}s before retry...", file=sys.stderr)
        time.sleep(delay)

        result = call_api(fallback_provider, fallback_model, messages, config, stream=stream)
        attempts.append({"provider": fallback_provider, "model": fallback_model, "status": result.get("status")})

        if result["success"]:
            result["provider"] = fallback_provider
            result["fallback"] = True
            result["attempts"] = attempts
            return result

        if result["status"] in (401, 403):
            break

    result["provider"] = fallback_provider
    result["fallback"] = True
    result["attempts"] = attempts
    return result


def print_stream_response(response, verbose=False, provider=None, fallback=False):
    """Print streaming SSE response token by token."""
    if verbose:
        label = f"[{provider.title()}:fallback]" if fallback else f"[{provider.title()}]"
        print(label, end=" ", flush=True)

    for line in response.iter_lines(decode_unicode=True):
        if line and line.startswith("data: "):
            data = line[6:]
            if data.strip() == "[DONE]":
                break
            try:
                chunk = json.loads(data)
                delta = chunk.get("choices", [{}])[0].get("delta", {})
                content = delta.get("content", "")
                if content:
                    print(content, end="", flush=True)
            except json.JSONDecodeError:
                continue
    print()  # Final newline


def print_error(error_data):
    """Print error as JSON to stderr."""
    print(json.dumps(error_data, indent=2), file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Rate limit router for OpenCode Zen and OpenRouter")
    parser.add_argument("prompt", help="The user prompt to send")
    parser.add_argument("--model", "-m", required=True, help="Model ID (Zen or OpenRouter)")
    parser.add_argument("--system", "-s", help="System prompt")
    parser.add_argument("--no-stream", action="store_true", help="Disable streaming")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show which API is used")
    parser.add_argument("--config", "-c", help="Path to config.json")

    args = parser.parse_args()

    config = load_config(args.config)

    messages = []
    if args.system:
        messages.append({"role": "system", "content": args.system})
    messages.append({"role": "user", "content": args.prompt})

    stream = not args.no_stream

    result = route(args.model, messages, config, stream=stream, verbose=args.verbose)

    if result["success"]:
        if stream and "stream_response" in result:
            print_stream_response(
                result["stream_response"],
                verbose=args.verbose,
                provider=result.get("provider"),
                fallback=result.get("fallback", False)
            )
        else:
            if args.verbose:
                label = f"[{result['provider'].title()}:fallback]" if result.get("fallback") else f"[{result['provider'].title()}]"
                print(label, end=" ")
            print(result.get("content", ""))
        sys.exit(0)
    else:
        print_error({
            "error": True,
            "message": f"All providers exhausted after {len(result.get('attempts', []))} attempts",
            "attempts": result.get("attempts", [])
        })
        sys.exit(1)


if __name__ == "__main__":
    main()

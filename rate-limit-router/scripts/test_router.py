import json
import os
import sys
import tempfile
import pytest
from unittest.mock import patch, MagicMock

import requests

sys.path.insert(0, os.path.dirname(__file__))
from rate_limit_router import load_config, detect_provider, get_fallback, backoff_sleep, call_api, route, print_error, main


def test_load_config_from_file():
    """Config loads correctly from a JSON file."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "openrouter": {"base_url": "https://openrouter.ai/api/v1/chat/completions"},
        "fallback_map": {"big-pickle": "nvidia/nemotron-3-super-120b-a12b:free"},
        "reverse_map": {"nvidia/nemotron-3-super-120b-a12b:free": "big-pickle"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(config, f)
        f.flush()
        result = load_config(f.name)
    os.unlink(f.name)
    assert result == config


def test_load_config_missing_file():
    """Raises SystemExit when config file not found."""
    with pytest.raises(SystemExit):
        load_config("/nonexistent/path.json")


def test_detect_provider_zen():
    """Zen models have no colon."""
    assert detect_provider("big-pickle") == "zen"
    assert detect_provider("deepseek-v4-flash-free") == "zen"


def test_detect_provider_openrouter():
    """OpenRouter models contain a colon."""
    assert detect_provider("nvidia/nemotron-3-super-120b-a12b:free") == "openrouter"
    assert detect_provider("tencent/hy3:free") == "openrouter"


def test_get_fallback_zen_to_or():
    """Zen model maps to OpenRouter fallback."""
    config = {
        "fallback_map": {"big-pickle": "nvidia/nemotron-3-super-120b-a12b:free"},
        "reverse_map": {"nvidia/nemotron-3-super-120b-a12b:free": "big-pickle"}
    }
    assert get_fallback("big-pickle", config) == "nvidia/nemotron-3-super-120b-a12b:free"


def test_get_fallback_or_to_zen():
    """OpenRouter model maps to Zen fallback."""
    config = {
        "fallback_map": {"big-pickle": "nvidia/nemotron-3-super-120b-a12b:free"},
        "reverse_map": {"nvidia/nemotron-3-super-120b-a12b:free": "big-pickle"}
    }
    assert get_fallback("nvidia/nemotron-3-super-120b-a12b:free", config) == "big-pickle"


def test_get_fallback_no_mapping():
    """Unmapped model returns None."""
    config = {"fallback_map": {}, "reverse_map": {}}
    assert get_fallback("unknown-model", config) is None


def test_backoff_sleep_timing():
    """Backoff delays multiply correctly."""
    config = {"backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}}
    assert backoff_sleep(0, config) == 1   # attempt 0 → 1s
    assert backoff_sleep(1, config) == 2   # attempt 1 → 2s
    assert backoff_sleep(2, config) == 4   # attempt 2 → 4s
    assert backoff_sleep(3, config) == 8   # attempt 3 → 8s
    assert backoff_sleep(4, config) == 16  # attempt 4 → capped at max_delay


def test_call_api_success():
    """Successful API call returns content."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hello world", "reasoning_content": ""}}]
    }
    mock_response.iter_lines.return_value = iter([])

    with patch('rate_limit_router.requests.post', return_value=mock_response), \
         patch('rate_limit_router.get_api_key', return_value="test-key"):
        result = call_api("zen", "big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is True
    assert result["content"] == "Hello world"


def test_call_api_rate_limit():
    """429 returns rate_limited status."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.text = "Rate limited"

    with patch('rate_limit_router.requests.post', return_value=mock_response), \
         patch('rate_limit_router.get_api_key', return_value="test-key"):
        result = call_api("zen", "big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is False
    assert result["status"] == 429


def test_call_api_auth_error():
    """401 returns auth_error status, no retry."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    mock_response = MagicMock()
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"

    with patch('rate_limit_router.requests.post', return_value=mock_response), \
         patch('rate_limit_router.get_api_key', return_value="bad-key"):
        result = call_api("zen", "big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is False
    assert result["status"] == 401


def test_call_api_missing_key():
    """Missing API key raises ValueError."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    with patch('rate_limit_router.get_api_key', side_effect=ValueError("Missing ZEN_API_KEY")):
        with pytest.raises(ValueError):
            call_api("zen", "big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)


def test_call_api_network_exception():
    """Network error returns failure with retries."""
    config = {
        "zen": {"base_url": "https://opencode.ai/zen/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 2}
    }
    exc = requests.exceptions.ConnectionError("refused")
    with patch('rate_limit_router.requests.post', side_effect=exc), \
         patch('rate_limit_router.get_api_key', return_value="test-key"), \
         patch('rate_limit_router.time.sleep'):
        result = call_api("zen", "big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is False
    assert result["status"] == 0
    assert result["attempts"] == 3  # initial + 2 retries


def test_call_api_openrouter_headers():
    """OpenRouter provider includes HTTP-Referer and X-Title headers."""
    config = {
        "openrouter": {"base_url": "https://openrouter.ai/api/v1/chat/completions"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": "Hi", "reasoning_content": ""}}]
    }

    with patch('rate_limit_router.requests.post', return_value=mock_response) as mock_post, \
         patch('rate_limit_router.get_api_key', return_value="or-key"):
        result = call_api("openrouter", "nvidia/nemotron-3-super-120b-a12b:free",
                          [{"role": "user", "content": "Hi"}], config, stream=False)

    assert result["success"] is True
    headers = mock_post.call_args[1]["headers"]
    assert headers["HTTP-Referer"] == "https://opencode.ai"
    assert headers["X-Title"] == "Rate Limit Router"


def test_route_zen_success():
    """Zen succeeds on first try."""
    config = {
        "zen": {"base_url": "https://zen.test"},
        "openrouter": {"base_url": "https://or.test"},
        "fallback_map": {"big-pickle": "openrouter:free"},
        "reverse_map": {"openrouter:free": "big-pickle"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    with patch('rate_limit_router.call_api') as mock_call:
        mock_call.return_value = {"success": True, "content": "Hi", "status": 200}
        result = route("big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is True
    assert result["provider"] == "zen"
    assert mock_call.call_count == 1


def test_route_zen_429_fallback_to_or():
    """Zen 429 triggers fallback to OpenRouter."""
    config = {
        "zen": {"base_url": "https://zen.test"},
        "openrouter": {"base_url": "https://or.test"},
        "fallback_map": {"big-pickle": "openrouter:free"},
        "reverse_map": {"openrouter:free": "big-pickle"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    with patch('rate_limit_router.call_api') as mock_call, \
         patch('rate_limit_router.time.sleep'):
        mock_call.side_effect = [
            {"success": False, "status": 429, "error": "Rate limited"},
            {"success": True, "content": "Fallback response", "status": 200}
        ]
        result = route("big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is True
    assert result["provider"] == "openrouter"
    assert result["fallback"] is True
    assert mock_call.call_count == 2


def test_route_both_fail():
    """Both providers fail after retries returns error."""
    config = {
        "zen": {"base_url": "https://zen.test"},
        "openrouter": {"base_url": "https://or.test"},
        "fallback_map": {"big-pickle": "openrouter:free"},
        "reverse_map": {"openrouter:free": "big-pickle"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 2}
    }
    with patch('rate_limit_router.call_api') as mock_call, \
         patch('rate_limit_router.time.sleep'):
        mock_call.return_value = {"success": False, "status": 429, "error": "Rate limited"}
        result = route("big-pickle", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is False
    assert len(result["attempts"]) > 0


def test_route_openrouter_direct():
    """OpenRouter model ID tries OpenRouter first."""
    config = {
        "zen": {"base_url": "https://zen.test"},
        "openrouter": {"base_url": "https://or.test"},
        "fallback_map": {"big-pickle": "openrouter:free"},
        "reverse_map": {"openrouter:free": "big-pickle"},
        "backoff": {"initial_delay": 1, "max_delay": 16, "multiplier": 2, "max_retries": 3}
    }
    with patch('rate_limit_router.call_api') as mock_call:
        mock_call.return_value = {"success": True, "content": "Direct OR", "status": 200}
        result = route("openrouter:free", [{"role": "user", "content": "Hi"}], config, stream=False)
    assert result["success"] is True
    assert result["provider"] == "openrouter"
    assert mock_call.call_count == 1


def test_print_error_json():
    """Error output is valid JSON to stderr."""
    import io
    old_stderr = sys.stderr
    sys.stderr = buffer = io.StringIO()
    try:
        print_error({"error": True, "message": "test"})
        output = buffer.getvalue()
    finally:
        sys.stderr = old_stderr
    parsed = json.loads(output)
    assert parsed["error"] is True


def test_cli_args_required():
    """Missing --model argument exits with error."""
    with pytest.raises(SystemExit):
        sys.argv = ["rate_limit_router.py", "Hello"]
        main()

"""Tests for external-llm-router scripts/agent.py."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts/ to path so we can import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import agent


# ---------------------------------------------------------------------------
# resolve_api_key
# ---------------------------------------------------------------------------

class TestResolveApiKey:
    def test_explicit_key_returned(self):
        assert agent.resolve_api_key("sk-test", "ANY_VAR") == "sk-test"

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("MY_KEY", "env-val")
        assert agent.resolve_api_key(None, "MY_KEY") == "env-val"

    def test_no_key_raises(self, monkeypatch):
        monkeypatch.delenv("MISSING_KEY", raising=False)
        with pytest.raises(SystemExit, match="No API key"):
            agent.resolve_api_key(None, "MISSING_KEY")


# ---------------------------------------------------------------------------
# _detect_provider
# ---------------------------------------------------------------------------

class TestDetectProvider:
    def test_anthropic_url(self):
        assert agent._detect_provider("https://api.anthropic.com/v1/messages") == "anthropic"

    def test_openai_url(self):
        assert agent._detect_provider("https://api.openai.com/v1/chat/completions") == "openai"

    def test_opencode_url(self):
        assert agent._detect_provider("https://opencode.ai/zen/v1/chat/completions") == "openai"


# ---------------------------------------------------------------------------
# _load_dotenv
# ---------------------------------------------------------------------------

class TestLoadDotenv:
    def test_loads_env_file(self, tmp_path):
        env_file = tmp_path / ".env"
        env_file.write_text('TEST_DOTENV_KEY="hello world"\n')
        agent._load_dotenv(tmp_path)
        assert os.environ.get("TEST_DOTENV_KEY") == "hello world"
        # Cleanup
        os.environ.pop("TEST_DOTENV_KEY", None)

    def test_does_not_override_existing(self, monkeypatch):
        monkeypatch.setenv("EXISTING_KEY", "original")
        env_file = Path(__file__).parent / ".env_test_fake"
        env_file.write_text('EXISTING_KEY=overridden\n')
        try:
            agent._load_dotenv(env_file.parent)
            assert os.environ["EXISTING_KEY"] == "original"
        finally:
            env_file.unlink(missing_ok=True)
            os.environ.pop("EXISTING_KEY", None)


# ---------------------------------------------------------------------------
# reset_usage_file
# ---------------------------------------------------------------------------

class TestResetUsageFile:
    def test_creates_fresh_file(self, tmp_path):
        usage_file = tmp_path / "usage.json"
        agent.reset_usage_file(str(usage_file))
        data = json.loads(usage_file.read_text())
        assert data["total"] == 0
        assert data["date"] == ""


# ---------------------------------------------------------------------------
# call_model (mocked HTTP)
# ---------------------------------------------------------------------------

class TestCallModel:
    @patch("agent._request_with_retry")
    def test_openai_success(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "choices": [{"message": {"content": "Hello!", "reasoning_content": "Thinking..."}}]
        }
        mock_req.return_value = mock_resp

        result = agent.call_model("sk-test", "https://api.openai.com/v1/chat/completions",
                                  "gpt-4o", "Hi")
        assert result["success"] is True
        assert result["content"] == "Hello!"
        assert result["reasoning"] == "Thinking..."

    @patch("agent._request_with_retry")
    def test_anthropic_success(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {
            "content": [{"type": "text", "text": "Anthropic response"}]
        }
        mock_req.return_value = mock_resp

        result = agent.call_model("sk-test", "https://api.anthropic.com/v1/messages",
                                  "claude-sonnet-4-20250514", "Hi")
        assert result["success"] is True
        assert result["content"] == "Anthropic response"
        assert result["reasoning"] == ""

    @patch("agent._request_with_retry")
    def test_http_error(self, mock_req):
        mock_resp = MagicMock()
        mock_resp.status_code = 401
        mock_resp.text = "Unauthorized"
        mock_req.return_value = mock_resp

        result = agent.call_model("bad-key", "https://api.openai.com/v1/chat/completions",
                                  "gpt-4o", "Hi")
        assert result["success"] is False
        assert "401" in result["error"]


# ---------------------------------------------------------------------------
# _request_with_retry
# ---------------------------------------------------------------------------

class TestRequestWithRetry:
    @patch("agent.time.sleep")
    @patch("agent.requests.request")
    def test_retries_on_429(self, mock_req, mock_sleep):
        fail_resp = MagicMock()
        fail_resp.status_code = 429
        fail_resp.headers = {"Retry-After": "0.1"}
        ok_resp = MagicMock()
        ok_resp.status_code = 200
        mock_req.side_effect = [fail_resp, ok_resp]

        resp = agent._request_with_retry("POST", "http://test",
                                          headers={}, json_data={})
        assert resp.status_code == 200
        assert mock_req.call_count == 2

    @patch("agent.time.sleep")
    @patch("agent.requests.request")
    def test_retries_on_connection_error(self, mock_req, mock_sleep):
        import requests as _requests
        mock_req.side_effect = _requests.ConnectionError("refused")

        with pytest.raises(_requests.ConnectionError):
            agent._request_with_retry("POST", "http://test",
                                       headers={}, json_data={},
                                       max_retries=2)
        assert mock_req.call_count == 2

# Provider Setup Guide

Detailed instructions for configuring each supported LLM provider.

---

## OpenCode Zen

OpenCode Zen provides free and paid models through a unified OpenAI-compatible API.

### Obtain an API Key

1. Sign up at [opencode.ai](https://opencode.ai).
2. Navigate to **Settings → API Keys** and generate a key.
3. Copy the key (starts with `oc_`).

### Configure

```bash
export OPENCODE_API_KEY="oc_..."
```

Or add to `.env`:

```
OPENCODE_API_KEY=oc_...
```

### Endpoint

| Item | Value |
|------|-------|
| Base URL | `https://opencode.ai/zen/v1` |
| Chat Completions | `https://opencode.ai/zen/v1/chat/completions` |
| Auth header | `Authorization: Bearer <key>` |

### Available Models

| Model ID | Description |
|----------|-------------|
| `opencode/big-pickle` | Flagship reasoning model |
| `opencode/north-mini-code-free` | Free code-focused model |
| `opencode/nemotron-3-ultra-free` | Free general-purpose model |
| `opencode/deepseek-v4-flash-free` | Free fast-inference model |
| `opencode/mimo-v2.5-free` | Free Xiaomi MiMo model |
| `opencode/ling-3.0-flash-free` | Free fast model |

---

## OpenAI

### Obtain an API Key

1. Go to [platform.openai.com](https://platform.openai.com).
2. Navigate to **API Keys** and create a new secret key.

### Configure

```bash
export OPENAI_API_KEY="sk-..."
```

### Endpoint

| Item | Value |
|------|-------|
| Base URL | `https://api.openai.com/v1` |
| Chat Completions | `https://api.openai.com/v1/chat/completions` |
| Auth header | `Authorization: Bearer <key>` |

### Popular Models

- `gpt-4o` — Multimodal flagship
- `gpt-4o-mini` — Fast, cost-effective
- `o3-mini` — Reasoning model

---

## OpenRouter

OpenRouter proxies access to hundreds of models from various providers.

### Obtain an API Key

1. Go to [openrouter.ai](https://openrouter.ai).
2. Create an account and generate an API key.

### Configure

```bash
export OPENROUTER_API_KEY="sk-or-..."
```

### Endpoint

| Item | Value |
|------|-------|
| Base URL | `https://openrouter.ai/api/v1` |
| Chat Completions | `https://openrouter.ai/api/v1/chat/completions` |
| Auth header | `Authorization: Bearer <key>` |

### Notes

- Set `HTTP-Referer` and `X-Title` headers for app attribution.
- Pricing varies per model — check [openrouter.ai/models](https://openrouter.ai/models).

---

## Anthropic

### Obtain an API Key

1. Go to [console.anthropic.com](https://console.anthropic.com).
2. Navigate to **API Keys** and create one.

### Configure

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

### Endpoint

| Item | Value |
|------|-------|
| Base URL | `https://api.anthropic.com/v1` |
| Messages API | `https://api.anthropic.com/v1/messages` |
| Auth header | `x-api-key: <key>` |
| API version | `anthropic-version: 2023-06-01` |

### Notes

- Anthropic uses a different request/response format (not OpenAI-compatible).
- The `agent.py` script auto-detects this from the URL.
- System prompt is passed as a top-level `system` field, not a message.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `401 Unauthorized` | Verify the API key is correct and not expired |
| `429 Too Many Requests` | Implement backoff; the agent retries 3 times automatically |
| `403 Forbidden` | Check your account has billing set up or the model is accessible |
| Connection timeout | Verify network/proxy settings; check the URL is correct |

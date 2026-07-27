import requests
import os

api_key = os.environ.get("OPENCODE_API_KEY", "")

def test_free_model():
    print("Testing North Mini Code (Free)...")
    url = "https://opencode.ai/zen/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "opencode/north-mini-code-free",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(response.text)

test_free_model()

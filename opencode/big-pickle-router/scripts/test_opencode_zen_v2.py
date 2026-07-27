import requests
import os

api_key = os.environ.get("OPENCODE_API_KEY", "")

def test_claude():
    print("Testing Big Pickle...")
    url = "https://opencode.ai/zen/v1/messages"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "opencode/big-pickle",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(response.text)

def test_gpt():
    print("\nTesting Ling 3.0 Flash (Free)...")
    url = "https://opencode.ai/zen/v1/responses"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "opencode/ling-3.0-flash-free",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 50
    }
    response = requests.post(url, headers=headers, json=data)
    print(f"Status: {response.status_code}")
    print(response.text)

test_claude()
test_gpt()

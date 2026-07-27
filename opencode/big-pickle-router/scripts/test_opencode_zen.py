import requests
import os

api_key = os.environ.get("OPENCODE_API_KEY", "")
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

url = "https://opencode.ai/zen/v1/chat/completions"
data = {
    "model": "opencode/mimo-v2.5-free",
    "messages": [{"role": "user", "content": "Hello, are you active?"}],
    "max_tokens": 50
}

try:
    response = requests.post(url, headers=headers, json=data)
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        print("Success! Response:")
        print(response.json()['choices'][0]['message']['content'])
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"An error occurred: {e}")

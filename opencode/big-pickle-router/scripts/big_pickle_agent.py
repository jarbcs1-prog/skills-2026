import requests
import sys
import json
import os

API_KEY = os.environ.get("OPENCODE_API_KEY", "")
URL = "https://opencode.ai/zen/v1/chat/completions"
MODEL = "opencode/big-pickle"

def call_big_pickle(prompt, context=None):
    if not API_KEY:
        raise ValueError("Set OPENCODE_API_KEY environment variable")

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if context:
        messages.extend(context)
    
    messages.append({"role": "user", "content": prompt})
    
    data = {
        "model": MODEL,
        "messages": messages,
        "stream": False
    }
    
    try:
        response = requests.post(URL, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message'].get('content', '')
            reasoning = result['choices'][0]['message'].get('reasoning_content', '')
            return {
                "success": True,
                "content": content,
                "reasoning": reasoning
            }
        else:
            return {
                "success": False,
                "error": response.text
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python big_pickle_agent.py 'your prompt here' [optional_context_json_file]")
        sys.exit(1)
    
    user_prompt = sys.argv[1]
    context_data = None
    
    if len(sys.argv) > 2:
        context_file = sys.argv[2]
        if os.path.exists(context_file):
            with open(context_file, 'r') as f:
                context_data = json.load(f)
    
    res = call_big_pickle(user_prompt, context_data)
    if res["success"]:
        if res["reasoning"]:
            print(f"--- REASONING ---\n{res['reasoning']}\n")
        print(f"--- RESPONSE ---\n{res['content']}")
    else:
        print(f"Error: {res['error']}")

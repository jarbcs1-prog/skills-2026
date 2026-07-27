import json
import os
from datetime import datetime

CONTEXT_FILE = "task_context.json"

def save_context(messages):
    """
    Saves the conversation context to a JSON file.
    'messages' should be a list of dicts: [{"role": "user/assistant", "content": "..."}]
    """
    data = {
        "last_updated": datetime.now().isoformat(),
        "history": messages
    }
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"Context saved to {CONTEXT_FILE}")

def load_context():
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r') as f:
            return json.load(f)
    return None

if __name__ == "__main__":
    # Example usage: script can be called to check status or manually trigger a save
    print("Delegation Manager Active.")
    if os.path.exists(CONTEXT_FILE):
        print(f"Current context file exists. Last updated: {load_context()['last_updated']}")
    else:
        print("No context file found.")

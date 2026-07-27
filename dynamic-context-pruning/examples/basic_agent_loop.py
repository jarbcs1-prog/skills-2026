import json
from scripts.context_monitor import ContextMonitor
from scripts.compaction import Compactor
from scripts.summarization import Summarizer, SummarySchema
from scripts.file_offloader import FileOffloader

# Dummy function to estimate tokens
def estimate_tokens(text):
    return len(text) // 4

async def basic_agent_step(context_history: list):
    # Load configuration (for simplicity, assume a default config or load from a fixed path)
    # In a real scenario, this would be loaded from .agent_context_config.json
    config = {
        "thresholds": {
            "hard_limit": 200000,
            "pre_rot_threshold": 100000,
            "compaction_trigger": 150000,
            "summarization_trigger": 175000
        },
        "compaction": {
            "strategy": "hybrid",
            "keep_recent_full": 5,
            "compact_ratio": 0.5,
            "preserve_structure": True
        },
        "summarization": {
            "schema": {
                "fields": ["user_goals", "current_state"],
                "required": ["user_goals", "current_state"]
            },
            "keep_recent_full": 3,
            "model": "opencode/big-pickle"
        },
        "offloading": {
            "base_path": ".agent_context",
            "compression": "gzip",
            "index_format": "jsonl"
        }
    }

    # For demonstration, we'll write this config to a temporary file
    config_path = ".agent_context_config.json"
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)

    monitor = ContextMonitor.from_config(config_path)
    compactor = Compactor.from_config(config_path)
    summarizer = Summarizer.from_config(config_path)
    offloader = FileOffloader.from_config(config_path)

    current_token_count = estimate_tokens(json.dumps(context_history))
    status = monitor.check_context(current_token_count)
    print(f"Current context status: {status}")

    if status["action"] == "compact":
        print("Triggering compaction...")
        compacted, offloaded = compactor.compact(context_history)
        ref = offloader.offload(offloaded, metadata={"phase": "compaction"})
        context_history = compacted + [{"type": "context_reference", "ref": ref}]
        print("Context compacted.")

    elif status["action"] == "summarize":
        print("Triggering summarization...")
        summary = summarizer.summarize(context_history[:-summarizer.keep_recent_full])
        ref = offloader.offload(context_history[:-summarizer.keep_recent_full], metadata={"phase": "summarization"})
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + context_history[-summarizer.keep_recent_full:]
        print("Context summarized.")

    return context_history

# Example usage:
if __name__ == "__main__":
    import asyncio
    initial_context = [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello! How can I help you?"}
    ]
    # Add some more context to simulate a long conversation
    for i in range(500):
        initial_context.append({"role": "user", "content": f"User message {i}"})
        initial_context.append({"role": "assistant", "content": f"Assistant response {i}"})

    print(f"Initial context length: {len(json.dumps(initial_context)) // 4} tokens")
    
    # Run a few steps to see pruning in action
    async def run_simulation():
        current_context = list(initial_context) # Create a mutable copy
        for _ in range(3):
            current_context = await basic_agent_step(current_context)
            print(f"Context length after step: {len(json.dumps(current_context)) // 4} tokens")
            print("--------------------------------------------------")

    asyncio.run(run_simulation())

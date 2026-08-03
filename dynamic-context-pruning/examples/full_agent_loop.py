import json
from scripts.context_monitor import ContextMonitor
from scripts.compaction import Compactor
from scripts.summarization import Summarizer
from scripts.file_offloader import FileOffloader
from scripts.kv_cache import KVCacheOptimizer

# Dummy function to estimate tokens
def estimate_tokens(obj):
    return len(json.dumps(obj)) // 4

async def full_agent_loop(context_history: list):
    # Load configuration from a dedicated file
    config_path = ".agent_context_config.json"
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: Configuration file {config_path} not found. Using default values.")
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
                "preserve_structure": True,
                "importance_weights": {
                    "user_goals": 1.0,
                    "errors": 0.9,
                    "key_decisions": 0.8,
                    "tool_outputs": 0.5,
                    "intermediate_steps": 0.3
                }
            },
            "summarization": {
                "schema": {
                    "fields": [
                        "files_modified",
                        "user_goals", 
                        "current_state",
                        "pending_actions",
                        "errors_encountered",
                        "key_decisions"
                    ],
                    "required": ["user_goals", "current_state"]
                },
                "keep_recent_full": 3,
                "model": "opencode/big-pickle"
            },
            "offloading": {
                "base_path": ".agent_context",
                "compression": "gzip",
                "index_format": "jsonl"
            },
            "kv_cache": {
                "enforce_stable_prefix": True,
                "append_only": True,
                "deterministic_json": True
            }
        }
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)

    monitor = ContextMonitor.from_config(config_path)
    compactor = Compactor.from_config(config_path)
    summarizer = Summarizer.from_config(config_path)
    offloader = FileOffloader.from_config(config_path)
    kv_optimizer = KVCacheOptimizer()

    # 1. KV-Cache Optimization (Pre-processing)
    if config["kv_cache"]["enforce_stable_prefix"] or config["kv_cache"]["append_only"] or config["kv_cache"]["deterministic_json"]:
        kv_issues = kv_optimizer.validate(context_history)
        if kv_issues:
            print(f"KV-Cache issues detected: {kv_issues}. Attempting to fix...")
            context_history = kv_optimizer.fix(context_history)

    # 2. Check context health
    current_token_count = estimate_tokens(context_history)
    status = monitor.check_context(current_token_count)
    print(f"Current context status: {status}")

    if status["action"] == "compact":
        print("Triggering compaction...")
        compacted, offloaded = compactor.compact(context_history)
        if offloaded:
            ref = offloader.offload(offloaded, metadata={"phase": "compaction", "tokens_before": estimate_tokens(offloaded)})
            context_history = compacted + [{"type": "context_reference", "ref": ref}]
        else:
            context_history = compacted
        print(f"Context compacted. New length: {estimate_tokens(context_history)} tokens")

    elif status["action"] == "summarize":
        print("Triggering summarization...")
        # Keep recent full messages for summarization context
        summarize_target = context_history[:-summarizer.keep_recent_full]
        recent_messages = context_history[-summarizer.keep_recent_full:]

        summary = summarizer.summarize(summarize_target)
        ref = offloader.offload(summarize_target, metadata={"phase": "summarization", "tokens_before": estimate_tokens(summarize_target)})
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + recent_messages
        print(f"Context summarized. New length: {estimate_tokens(context_history)} tokens")

    elif status["action"] == "critical":
        print("CRITICAL: Context hard limit reached. Forcing summarization and offloading.")
        # Force summarization and offloading in critical state
        summarize_target = context_history[:-summarizer.keep_recent_full]
        recent_messages = context_history[-summarizer.keep_recent_full:]

        summary = summarizer.summarize(summarize_target)
        ref = offloader.offload(summarize_target, metadata={"phase": "critical_summarization", "tokens_before": estimate_tokens(summarize_target)})
        context_history = [{"type": "summary", "data": summary}, {"type": "context_reference", "ref": ref}] + recent_messages
        print(f"Context critically reduced. New length: {estimate_tokens(context_history)} tokens")

    return context_history

# Example usage:
if __name__ == "__main__":
    import asyncio
    initial_context = [
        {"role": "system", "content": "You are a helpful AI assistant."},
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hello! How can I help you?"}
    ]
    # Add a lot of context to simulate a long conversation
    for i in range(5000):
        initial_context.append({"role": "user", "content": f"User message {i} - This is a somewhat long message to simulate real-world context growth."})
        initial_context.append({"role": "assistant", "content": f"Assistant response {i} - This is also a somewhat long response, providing details and observations."})

    print(f"Initial context length: {estimate_tokens(initial_context)} tokens")
    
    async def run_full_simulation():
        current_context = list(initial_context) # Create a mutable copy
        for step in range(5):
            print(f"\n--- Agent Step {step + 1} ---")
            current_context = await full_agent_agent_loop(current_context)
            print(f"Context length after step {step + 1}: {estimate_tokens(current_context)} tokens")
            print("--------------------------------------------------")

    asyncio.run(run_full_simulation())

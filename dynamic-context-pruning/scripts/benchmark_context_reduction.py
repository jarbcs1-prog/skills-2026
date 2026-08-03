"""
Benchmark Context Reduction — Performance benchmarks for context pruning operations.
"""

import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any
import random
import string

from context_monitor import ContextMonitor
from compaction import Compactor, CompactionConfig, CompactionStrategy
from summarization import Summarizer, SummarizationConfig, SCHEMAS
from file_offloader import FileOffloader, OffloaderConfig
from token_estimator import estimate_context_tokens


def generate_large_context(num_entries: int = 1000) -> List[Dict[str, Any]]:
    """Generate a large context for benchmarking."""
    entry_types = ["user_message", "assistant_message", "tool_call", "tool_result", "system_prompt"]
    tools = ["read_file", "write_file", "edit_file", "run_tests", "search_files", "grep"]
    
    context = [{"type": "system_prompt", "content": "You are a helpful coding assistant."}]
    
    for i in range(num_entries - 1):
        entry_type = random.choice(entry_types)
        
        if entry_type == "user_message":
            context.append({
                "type": "user_message",
                "role": "user",
                "content": f"Task {i}: {' '.join(random.choices(string.ascii_words, k=20))}",
            })
        elif entry_type == "assistant_message":
            context.append({
                "type": "assistant_message",
                "content": f"Response {i}: {' '.join(random.choices(string.ascii_words, k=50))}",
            })
        elif entry_type == "tool_call":
            tool = random.choice(tools)
            context.append({
                "type": "tool_call",
                "tool": tool,
                "arguments": {"param": f"value_{i}"},
                "output": f"Output {i}: {' '.join(random.choices(string.ascii_words, k=100))}",
            })
        elif entry_type == "tool_result":
            context.append({
                "type": "tool_result",
                "tool": random.choice(tools),
                "result": f"Result {i}: {' '.join(random.choices(string.ascii_words, k=100))}",
            })
    
    return context


def benchmark_context_monitor(context: List[Dict[str, Any]], iterations: int = 100) -> Dict[str, float]:
    """Benchmark context monitoring."""
    monitor = ContextMonitor(
        hard_limit=256_000,
        pre_rot_threshold=100_000,
        compaction_trigger=150_000,
        summarization_trigger=175_000,
    )
    
    tokens = estimate_context_tokens(context)
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        monitor.check_context(tokens)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # ms
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "iterations": iterations,
    }


def benchmark_compaction(context: List[Dict[str, Any]], strategy: CompactionStrategy, iterations: int = 50) -> Dict[str, float]:
    """Benchmark compaction strategy."""
    config = CompactionConfig(
        strategy=strategy,
        keep_recent_full=5,
        compact_ratio=0.5,
    )
    compactor = Compactor(config)
    
    times = []
    tokens_saved = []
    for _ in range(iterations):
        start = time.perf_counter()
        result = compactor.compact(context)
        end = time.perf_counter()
        times.append((end - start) * 1000)
        tokens_saved.append(result.tokens_saved)
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "mean_tokens_saved": statistics.mean(tokens_saved),
        "iterations": iterations,
    }


def benchmark_summarization(context: List[Dict[str, Any]], schema_name: str, iterations: int = 20) -> Dict[str, float]:
    """Benchmark summarization with a schema."""
    schema = SCHEMAS[schema_name]
    config = SummarizationConfig(schema=schema, keep_recent_full=3)
    summarizer = Summarizer(config)
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        summarizer.summarize(context)
        end = time.perf_counter()
        times.append((end - start) * 1000)
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "iterations": iterations,
    }


def benchmark_offloading(context: List[Dict[str, Any]], iterations: int = 30) -> Dict[str, float]:
    """Benchmark file offloading."""
    import tempfile
    
    offloader = FileOffloader(OffloaderConfig(
        base_path=tempfile.gettempdir() + "/benchmark_offload",
        compression="gzip",
        index_format="jsonl",
    ))
    
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        ref = offloader.offload(context, metadata={"type": "benchmark", "range": "0-100"})
        end = time.perf_counter()
        times.append((end - start) * 1000)
        
        # Cleanup
        Path(ref.path).unlink(missing_ok=True)
    
    return {
        "mean_ms": statistics.mean(times),
        "median_ms": statistics.median(times),
        "stdev_ms": statistics.stdev(times) if len(times) > 1 else 0,
        "min_ms": min(times),
        "max_ms": max(times),
        "iterations": iterations,
    }


def run_full_benchmark():
    """Run complete benchmark suite."""
    print("="*70)
    print("CONTEXT PRUNING BENCHMARK")
    print("="*70)
    
    # Generate test contexts
    print("\nGenerating test contexts...")
    small_context = generate_large_context(100)
    medium_context = generate_large_context(500)
    large_context = generate_large_context(2000)
    
    for name, ctx in [("Small (100)", small_context), ("Medium (500)", medium_context), ("Large (2000)", large_context)]:
        tokens = estimate_context_tokens(ctx)
        print(f"  {name}: {len(ctx)} entries, ~{tokens} tokens")
    
    results = {}
    
    # Benchmark Context Monitor
    print("\n📊 Benchmarking Context Monitor...")
    for name, ctx in [("Small", small_context), ("Medium", medium_context), ("Large", large_context)]:
        results[f"monitor_{name}"] = benchmark_context_monitor(ctx)
        print(f"  {name}: {results[f'monitor_{name}']['mean_ms']:.2f} ms")
    
    # Benchmark Compaction Strategies
    print("\n📦 Benchmarking Compaction Strategies...")
    strategies = [
        CompactionStrategy.TOKEN_BUDGET,
        CompactionStrategy.AGE_BASED,
        CompactionStrategy.IMPORTANCE_BASED,
        CompactionStrategy.HYBRID,
        CompactionStrategy.TIMESTAMP_HIDING,
        CompactionStrategy.HEAD_TAIL_PROTECTION,
        CompactionStrategy.REPEATED_TOOL_PRUNING,
        CompactionStrategy.ERROR_PRESERVATION,
    ]
    
    for strategy in strategies:
        print(f"  Testing {strategy.value}...")
        results[f"compact_{strategy.value}"] = benchmark_compaction(medium_context, strategy)
        print(f"    Mean: {results[f'compact_{strategy.value}']['mean_ms']:.2f} ms, Tokens saved: {results[f'compact_{strategy.value}']['mean_tokens_saved']:.0f}")
    
    # Benchmark Summarization Schemas
    print("\n📝 Benchmarking Summarization Schemas...")
    for schema_name in SCHEMAS.keys():
        print(f"  Testing {schema_name}...")
        results[f"summarize_{schema_name}"] = benchmark_summarization(medium_context, schema_name)
        print(f"    Mean: {results[f'summarize_{schema_name}']['mean_ms']:.2f} ms")
    
    # Benchmark Offloading
    print("\n💾 Benchmarking File Offloading...")
    results["offloading"] = benchmark_offloading(medium_context)
    print(f"  Mean: {results['offloading']['mean_ms']:.2f} ms")
    
    # Summary
    print("\n" + "="*70)
    print("BENCHMARK SUMMARY")
    print("="*70)
    
    print("\nContext Monitor (ms):")
    for name in ["Small", "Medium", "Large"]:
        r = results[f"monitor_{name}"]
        print(f"  {name:6}: {r['mean_ms']:.2f} ± {r['stdev_ms']:.2f}")
    
    print("\nCompaction Strategies (ms, tokens saved):")
    for strategy in strategies:
        r = results[f"compact_{strategy.value}"]
        print(f"  {strategy.value:25}: {r['mean_ms']:6.2f} ± {r['stdev_ms']:5.2f}  Tokens: {r['mean_tokens_saved']:>10.0f}")
    
    print("\nSummarization Schemas (ms):")
    for schema_name in SCHEMAS.keys():
        r = results[f"summarize_{schema_name}"]
        print(f"  {schema_name:20}: {r['mean_ms']:6.2f} ± {r['stdev_ms']:5.2f}")
    
    print("\nFile Offloading (ms):")
    r = results["offloading"]
    print(f"  Offload: {r['mean_ms']:.2f} ± {r['stdev_ms']:.2f}")
    
    # Save results
    with open("benchmark_results.json", "w") as f:
        json.dump(results, f, indent=2)
    print("\n📁 Results saved to benchmark_results.json")
    
    return results


if __name__ == "__main__":
    run_full_benchmark()
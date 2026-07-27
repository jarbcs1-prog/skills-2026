# OpenCode Context Engineering Principles

This document details OpenCode's specific techniques for context engineering, optimized for long-running coding agents:

1.  **Timestamp-Based Message Hiding (Native Compaction):** OpenCode's native compaction agent uses a non-destructive, timestamp-based approach to hide messages from the LLM's view without physically deleting them. This allows for easy restoration if the context needs to be revisited, unlike physical deletion.

2.  **Head/Tail Token Budgeting (Tier 1 Reduction):** To prevent "garbage" context from entering the window, OpenCode (and similar agents like Codex) implement strict token budgets for tool outputs. If an output exceeds the budget, the system keeps the critical "Head" (context) and "Tail" (results/errors), aggressively pruning the middle. This is highly effective for noisy tool outputs like test suites.

3.  **Cache-Friendly Prefix Preservation (Tier 2 Reduction):** OpenCode strives to avoid modifying the first half of the message sequence. It takes a "surgical" approach: trimming only at the tail, ensuring the beginning of the message sequence remains absolutely consistent. The trade-off is slightly lower cleanup efficiency, but the payoff is maximized Prompt Cache hit rate, dramatically reducing cost and latency.

4.  **Structured 5-Heading Summarization (Tier 3 Reduction):** When hiding and pruning are insufficient, OpenCode triggers a full summary. Unlike generic summaries, OpenCode uses a structured 5-heading approach (Current State, Completed Actions, Pending Actions, Key Decisions, Errors Encountered) to ensure the LLM retains the exact information needed to resume work without hallucinating.

5.  **Protected Tool Outputs:** OpenCode (and plugins like DCP) protect specific tool outputs from pruning. Tools like `task`, `skill`, `todowrite`, `todoread`, `compress`, `batch`, `plan_enter`, `plan_exit`, `write` and `edit` are never pruned to ensure critical workflow state and file changes are never lost.

6.  **Error Preservation:** OpenCode's context pruning logic specifically handles errors. It prunes errored tool call inputs after a configurable number of turns, but *always* preserves the error messages themselves. This ensures the agent knows exactly what went wrong and can attempt to fix it.

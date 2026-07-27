# Context Engineering Principles

This document details six key techniques for context engineering:

1.  **KV-cache optimization through stable prefixes and append-only context:** Ensuring that the context provided to the model is structured in a way that maximizes the efficiency of the Key-Value cache, leading to faster inference and reduced computational load. This involves maintaining stable prefixes in the prompt and ensuring that new information is appended rather than inserted or modified within existing context.

2.  **Tool masking via logit manipulation (not tool removal):** Instead of physically removing tools from the agent's available set, this technique involves manipulating the model's logits to reduce the probability of selecting irrelevant tools in specific contexts. This allows for dynamic control over tool usage without altering the underlying tool definitions.

3.  **File system as external memory with restorable compression:** Utilizing the file system as a persistent, external memory store for context. Information can be compressed and offloaded to files, with mechanisms in place to restore the original context when needed. This effectively extends the agent's working memory beyond the immediate context window.

4.  **Staged reduction: compaction first, summarization only when needed:** A hierarchical approach to context reduction. The first stage involves 
compaction, which is a reversible process of reducing detail while preserving structure. Only if compaction is insufficient, the second stage, irreversible summarization, is employed.

5.  **Attention management via todo.md recitation:** The `todo.md` file serves as a focal point for the agent's attention. By periodically 
reciting or referencing the `todo.md` file, the agent can re-focus its attention on critical tasks and objectives, preventing context drift.

6.  **Controlled diversity to prevent context rot:** Actively managing the diversity of information within the context to prevent it from becoming stale or overly focused on a narrow set of topics. This can involve techniques like periodically injecting new, relevant information or rotating older context elements to maintain a broad understanding.

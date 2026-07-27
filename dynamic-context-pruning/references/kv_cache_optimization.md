# KV-Cache Optimization

This document details the principles for optimizing the Key-Value (KV) cache in large language models within the context of AI agents. Efficient KV-cache utilization is crucial for reducing computational overhead and improving inference speed, especially in long-running agentic loops.

## KV-Cache Rules:

1.  **Stable Prompt Prefix**: The initial part of the prompt or the "prefix," should remain stable and consistent across turns. Any dynamic content, such as timestamps, session IDs or rapidly changing environmental variables, should be placed after this stable prefix. Modifying the prefix invalidates the KV-cache, forcing a re-computation of keys and values for the entire prompt history.

2.  **Append-Only Context**: New information should always be appended to the end of the context. Modifying or inserting content into previous messages or observations breaks the append-only nature of the context, leading to KV-cache invalidation. If a correction or update is necessary, it should be added as a new message, referencing the item being corrected.

3.  **Deterministic Serialization**: When serializing structured data (e.g. JSON objects) into the context, ensure that the serialization process is deterministic. This means that the same data should always produce the exact same string representation. For JSON, this often involves sorting keys alphabetically (`json.dumps(..., sort_keys=True)`). Non-deterministic serialization can lead to subtle changes in the context that invalidate the KV-cache.

4.  **Explicit Cache Breakpoints**: In scenarios where a complete context reset or a significant change in the agent's state is unavoidable, explicitly mark these as "cache breakpoints." This signals that the KV-cache should be cleared or re-initialized from this point, preventing the model from attempting to use an invalidated cache and potentially generating incoherent responses.

## Common KV-Cache Breaking Issues:

-   **Non-deterministic JSON serialization**: Using `json.dumps()` without `sort_keys=True` can lead to different string outputs for the same dictionary, breaking cache consistency.
-   **Timestamps in prefix**: Including dynamic timestamps or other volatile data in the initial system prompt or early messages.
-   **Modified previous messages**: Editing or re-writing past agent actions or observations in the context history.
-   **Unstable tool definitions**: If tool definitions or their descriptions change frequently, this can also impact cache stability if they are part of the persistent context.

## Optimization Strategies:

-   **Separate dynamic and static context**: Keep static, unchanging information (e.g. core instructions, persona) in a separate, stable prefix. Dynamic information (e.g. current task, recent observations) can then be appended.
-   **Batching and chunking**: For large inputs, process them in chunks that fit within the cache-friendly window, summarizing or offloading as needed.
-   **Context hashing**: Implement a mechanism to hash context segments and only re-compute KV-cache when the hash changes, indicating a true modification.

By adhering to these principles, AI agents can maintain a highly efficient KV-cache, leading to more performant and cost-effective operations.

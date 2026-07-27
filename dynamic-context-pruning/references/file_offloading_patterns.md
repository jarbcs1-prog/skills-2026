# File Offloading Patterns

This document outlines the best practices and rules for offloading context to the filesystem with restorable references, a core component of the Dynamic Context Pruning Skill.

## Restorable Compression Rules:

1.  **Web content → drop HTML, keep URL**: When offloading web pages, the verbose HTML content should be dropped. Instead, only the original URL should be preserved. This allows for restoration by re-fetching the URL if the full content is ever needed again, significantly reducing storage and context size.

2.  **Document content → drop text, keep file path**: For large documents (e.g. PDFs, Word documents), the full textual content can be offloaded. The original file path (or a reference to its location in a persistent storage) should be retained. If the document content is required, it can be re-read from the file path.

3.  **Tool outputs → drop verbose output, keep structured result**: Many tools produce verbose logs or intermediate outputs. When offloading, prioritize keeping only the structured, essential results of the tool execution. The full verbose output can be stored separately and referenced if detailed debugging is ever necessary.

4.  **Always preserve: URLs, file paths, IDs, structured data**: These are the critical 
elements that enable restoration and re-contextualization. URLs provide direct access to web resources, file paths point to local or remote documents and IDs allow for unambiguous referencing of entities. Structured data, even when offloaded, should maintain its schema to ensure integrity upon restoration.

## Offloading Mechanisms:

-   **Compression**: Utilize efficient compression algorithms (e.g. gzip, zstd) to minimize storage footprint of offloaded data.
-   **Indexing**: Maintain an index (e.g. JSONL, SQLite) of offloaded context segments, including metadata such as type, original range, summary and token count. This index facilitates quick lookup and selective restoration.
-   **Versioning**: Implement versioning for offloaded context to track changes and allow rollback to previous states if needed.

## Integration with Agent Workflow:

-   **Automatic Offloading**: Integrate offloading into the agent loop, triggering it when context thresholds are approached or after significant task milestones.
-   **On-Demand Restoration**: Provide mechanisms for the agent to explicitly request restoration of offloaded context segments when they become relevant again.
-   **Reference Management**: Ensure that references to offloaded context are concise and informative, allowing the agent to understand what information is available externally without loading it into the full content.

# Compaction Strategies

This document outlines various strategies for reversible context reduction, as part of the Dynamic Context Pruning Skill.

## 1. Token Budget Allocation

This strategy involves allocating a specific token budget across different segments of the context history. For example, more recent interactions might be allocated a larger budget, while older interactions receive a smaller budget, leading to more aggressive compaction for older data.

## 2. Age-Based Compaction

In this strategy, the oldest `N%` of tool calls or context entries are targeted for compaction. This assumes that older information is generally less relevant than newer information. The compaction process for these older entries can involve reducing verbosity, removing redundant details or converting them into more concise representations.

## 3. Importance-Based Compaction

This strategy involves scoring context entries by their relevance or importance to the current task or overall goal. Entries with lower importance scores are then prioritized for compaction. Importance can be determined by factors such as:
-   **User goals**: Context directly related to the user's stated goals receives higher importance.
-   **Errors/Critical events**: Information pertaining to errors or critical system events is considered highly important.
-   **Key decisions**: Records of significant decisions made by the agent or user are preserved.
-   **Tool outputs**: Structured tool outputs might be more important than verbose intermediate logs.

## 4. Hybrid Compaction

The default strategy combines age-based and importance-based compaction. This approach allows for a balanced reduction of context, ensuring that both recent and important information is preserved, while older and less critical details are compacted. For instance, the oldest `X%` of context might be compacted, but within that `X%`, items with high importance scores are treated less aggressively or summarized instead of fully removed.

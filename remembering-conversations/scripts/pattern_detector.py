from __future__ import annotations

from scripts.conversation_index import ConversationIndex, tokenize

DECISION_LEXICON = {
    "choose",
    "decided",
    "decision",
    "refactor",
    "approach",
    "architect",
    "use",
    "adopt",
    "prefer",
    "recommend",
    "migrate",
    "implement",
    "strategy",
    "solution",
    "pattern",
}

ARCHITECTURE_LEXICON = {
    "architecture",
    "service",
    "api",
    "module",
    "class",
    "interface",
    "schema",
    "database",
    "cache",
    "queue",
    "event",
    "handler",
    "config",
    "cli",
    "client",
    "server",
    "package",
    "function",
}


class PatternDetector:
    def __init__(self, index: ConversationIndex):
        self.index = index

    @staticmethod
    def _text(conversation: dict) -> str:
        parts = [conversation.get("summary", "")]
        parts.extend(str(message.get("content", "")) for message in conversation.get("messages", []))
        return "\n".join(parts)

    def _term_stats(self, lexicon: set[str]) -> tuple[dict[str, int], dict[str, list[str]]]:
        counts: dict[str, int] = {}
        conversations: dict[str, list[str]] = {}
        for conversation_id in self.index.all_ids():
            conversation = self.index.get(conversation_id)
            if conversation is None:
                continue
            tokens = tokenize(self._text(conversation))
            for token in tokens:
                if token in lexicon:
                    counts[token] = counts.get(token, 0) + 1
            for token in set(tokens):
                if token in lexicon:
                    conversations.setdefault(token, []).append(conversation_id)
        return counts, conversations

    def _top_patterns(self, lexicon: set[str], top_k: int) -> list[dict]:
        counts, conversations = self._term_stats(lexicon)
        patterns = [
            {
                "term": term,
                "conversations": len(ids),
                "count": counts[term],
                "conversation_ids": sorted(ids),
            }
            for term, ids in conversations.items()
        ]
        patterns.sort(key=lambda item: (-item["count"], -item["conversations"], item["term"]))
        return patterns[:top_k]

    def detect_recurring_decisions(self, top_k: int = 10) -> list[dict]:
        return self._top_patterns(DECISION_LEXICON, top_k)

    def detect_architectural_patterns(self, top_k: int = 10) -> list[dict]:
        return self._top_patterns(ARCHITECTURE_LEXICON, top_k)

    def find_similar_situation(self, description: str, top_k: int = 5) -> list[dict]:
        return self.index.search(description, top_k=top_k)

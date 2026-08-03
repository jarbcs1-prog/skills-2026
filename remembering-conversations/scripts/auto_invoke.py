from __future__ import annotations

TRIGGER_PHRASES = [
    "how should i",
    "what's the best approach",
    "best way to",
    "recommended approach",
    "how do i",
    "what would you do",
    "last time we",
    "remember when",
    "you implemented",
    "we discussed",
]


def should_search(message: str) -> bool:
    message_lower = message.lower()
    return any(phrase in message_lower for phrase in TRIGGER_PHRASES)

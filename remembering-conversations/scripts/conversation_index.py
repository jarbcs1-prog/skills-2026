from __future__ import annotations

import hashlib
import json
import math
import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path

_MANIFEST_NAME = "index.json"

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "is",
    "it",
    "we",
    "i",
    "you",
    "with",
    "on",
    "at",
    "that",
    "this",
    "how",
    "what",
    "what's",
    "do",
    "does",
    "did",
}

_TOKEN_RE = re.compile(r"\w+")


def tokenize(text: str) -> list[str]:
    tokens = _TOKEN_RE.findall(str(text).lower())
    return [token for token in tokens if token not in STOPWORDS]


def _trigrams(text: str) -> set[str]:
    lowered = str(text).lower()
    length = len(lowered)
    if length == 0:
        return set()
    if length < 3:
        return {lowered}
    return {lowered[i : i + 3] for i in range(length - 2)}


def trigram_similarity(a: str, b: str) -> float:
    trigrams_a = _trigrams(a)
    trigrams_b = _trigrams(b)
    if not trigrams_a or not trigrams_b:
        return 0.0
    return len(trigrams_a & trigrams_b) / len(trigrams_a | trigrams_b)


class ConversationIndex:
    def __init__(self, cache_dir: Path | None = None):
        if cache_dir is None:
            cache_dir = Path(__file__).resolve().parent.parent / ".conversation_cache"
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> dict:
        default = {"conversations": {}, "queries": []}
        path = self.cache_dir / _MANIFEST_NAME
        if not path.exists():
            return default
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return default
        if not isinstance(data, dict):
            return default
        data.setdefault("conversations", {})
        data.setdefault("queries", [])
        return data

    def _save_manifest(self) -> None:
        (self.cache_dir / _MANIFEST_NAME).write_text(
            json.dumps(self._manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    @staticmethod
    def _safe_filename(conversation_id: str) -> str:
        base = re.sub(r"[^A-Za-z0-9_.-]", "_", conversation_id).strip("._")
        if not base:
            base = "conversation"
        return f"{base}.json"

    def _write_conversation(self, filename: str, record: dict) -> None:
        (self.cache_dir / filename).write_text(
            json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8"
        )

    def _read_conversation(self, filename: str) -> dict | None:
        path = self.cache_dir / filename
        if not path.exists():
            return None
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return None

    def add(self, conversation: dict) -> None:
        conversation_id = conversation.get("conversation_id")
        if not isinstance(conversation_id, str) or not conversation_id:
            raise ValueError("conversation must include a string conversation_id")
        if not isinstance(conversation.get("messages"), list):
            raise ValueError("conversation must include a messages list")
        existing = self._manifest["conversations"].get(conversation_id)
        if conversation.get("timestamp"):
            timestamp = str(conversation["timestamp"])
        elif existing:
            timestamp = existing["timestamp"]
        else:
            timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        if existing:
            filename = existing["file"]
        else:
            filename = self._safe_filename(conversation_id)
            files_in_use = {entry["file"] for entry in self._manifest["conversations"].values()}
            if filename in files_in_use:
                digest = hashlib.sha1(conversation_id.encode("utf-8")).hexdigest()[:8]
                filename = f"{Path(filename).stem}-{digest}.json"
        record = {
            "conversation_id": conversation_id,
            "timestamp": timestamp,
            "messages": list(conversation["messages"]),
            "tags": list(conversation.get("tags") or []),
            "summary": conversation.get("summary") or "",
        }
        self._write_conversation(filename, record)
        self._manifest["conversations"][conversation_id] = {
            "timestamp": timestamp,
            "file": filename,
        }
        self._save_manifest()

    def sync(self, export_dir: Path) -> int:
        export_dir = Path(export_dir)
        if not export_dir.is_dir():
            raise FileNotFoundError(f"export dir not found: {export_dir}")
        added = 0
        for path in sorted(export_dir.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if not isinstance(data, dict):
                continue
            if isinstance(data.get("conversations"), list):
                candidates = list(data["conversations"])
            elif isinstance(data.get("messages"), list):
                candidates = [data]
            else:
                continue
            for index, conversation in enumerate(candidates):
                if not isinstance(conversation, dict) or not isinstance(
                    conversation.get("messages"), list
                ):
                    continue
                if not conversation.get("conversation_id"):
                    conversation = dict(conversation)
                    suffix = index if len(candidates) > 1 else ""
                    conversation["conversation_id"] = f"{path.stem}{suffix}"
                if conversation["conversation_id"] in self._manifest["conversations"]:
                    continue
                self.add(conversation)
                added += 1
        return added

    def get(self, conversation_id: str) -> dict | None:
        entry = self._manifest["conversations"].get(conversation_id)
        if entry is None:
            return None
        return self._read_conversation(entry["file"])

    def get_summary(self, conversation_id: str) -> str | None:
        conversation = self.get(conversation_id)
        return conversation["summary"] if conversation else None

    def all_ids(self) -> list[str]:
        return sorted(self._manifest["conversations"])

    def recent(self, days: int = 30) -> list[str]:
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        return sorted(
            cid
            for cid, entry in self._manifest["conversations"].items()
            if entry["timestamp"][:10] >= cutoff
        )

    def _record_query(self, query: str) -> None:
        queries = self._manifest["queries"]
        queries.append(query)
        if len(queries) > 200:
            del queries[: len(queries) - 200]
        self._save_manifest()

    def top_queries(self, limit: int = 5) -> list[str]:
        counts: dict[str, int] = {}
        for query in self._manifest["queries"]:
            counts[query] = counts.get(query, 0) + 1
        ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        return [query for query, _ in ranked[:limit]]

    @staticmethod
    def _conversation_text(conversation: dict) -> str:
        parts = [conversation.get("summary", "")]
        parts.extend(str(message.get("content", "")) for message in conversation.get("messages", []))
        return "\n".join(parts)

    def search(
        self,
        query: str,
        since: str | None = None,
        top_k: int = 10,
    ) -> list[dict]:
        self._record_query(query)
        conversations = {
            cid: self.get(cid) for cid in self.all_ids() if self.get(cid) is not None
        }
        if since:
            conversations = {
                cid: conv
                for cid, conv in conversations.items()
                if str(conv.get("timestamp", ""))[:10] >= since
            }
        query_tokens = tokenize(query)
        if not conversations or not query_tokens:
            return []
        total_docs = len(conversations)
        doc_frequency: dict[str, int] = {}
        conversation_tokens: dict[str, list[str]] = {}
        for cid, conversation in conversations.items():
            tokens = tokenize(self._conversation_text(conversation))
            conversation_tokens[cid] = tokens
            for token in set(tokens):
                doc_frequency[token] = doc_frequency.get(token, 0) + 1
        idf = {
            token: 1 + math.log(total_docs / doc_frequency[token])
            for token in query_tokens
            if token in doc_frequency
        }
        results = []
        for cid, conversation in conversations.items():
            term_counts = Counter(conversation_tokens[cid])
            keyword_score = sum(term_counts[token] * idf[token] for token in idf)
            unique_contents = {
                str(message.get("content", "")) for message in conversation.get("messages", [])
            }
            ngram_score = max(
                (trigram_similarity(query, content) for content in unique_contents), default=0.0
            )
            best_messages: dict[str, dict] = {}
            for message in conversation.get("messages", []):
                content = str(message.get("content", ""))
                message_score = trigram_similarity(query, content)
                if message_score > 0 and content not in best_messages:
                    best_messages[content] = {
                        "role": message.get("role", ""),
                        "content": content,
                        "score": message_score,
                    }
            matched = sorted(
                best_messages.values(), key=lambda item: (-item["score"], item["role"], item["content"])
            )
            results.append(
                {
                    "conversation_id": cid,
                    "score": 0.7 * keyword_score + 0.3 * ngram_score,
                    "summary": conversation.get("summary", ""),
                    "matched_messages": matched[:5],
                }
            )
        results.sort(key=lambda item: (-item["score"], item["conversation_id"]))
        return results[:top_k]

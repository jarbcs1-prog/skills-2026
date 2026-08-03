"""
File Offloader — Filesystem offloading with restorable references.
"""

import json
import gzip
import hashlib
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class OffloadMetadata:
    type: str  # "tool_calls", "context_segment", "summary", etc.
    range: str  # e.g., "0-25"
    summary: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    platform: str = "generic"
    compression: str = "gzip"
    index_format: str = "jsonl"


@dataclass
class OffloadReference:
    path: str
    url: str
    tokens: int
    metadata: OffloadMetadata
    sha256: str


@dataclass
class OffloaderConfig:
    base_path: str = ".agent_context"
    compression: str = "gzip"
    index_format: str = "jsonl"


class FileOffloader:
    """Offloads context segments to filesystem with restorable references."""

    def __init__(self, config: OffloaderConfig):
        self.config = config
        self.base_path = Path(config.base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.index_path = self.base_path / "index.jsonl"

    @classmethod
    def from_config(cls, config_path: str) -> "FileOffloader":
        with open(config_path) as f:
            config_data = json.load(f)
        offload_config = config_data.get("offloading", {})
        return cls(OffloaderConfig(
            base_path=offload_config.get("base_path", ".agent_context"),
            compression=offload_config.get("compression", "gzip"),
            index_format=offload_config.get("index_format", "jsonl"),
        ))

    def _compute_hash(self, data: Any) -> str:
        """Compute SHA256 hash of data."""
        serialized = json.dumps(data, sort_keys=True).encode()
        return hashlib.sha256(serialized).hexdigest()

    def _estimate_tokens(self, data: Any) -> int:
        """Rough token estimation."""
        return len(json.dumps(data, sort_keys=True)) // 4

    def _write_compressed(self, path: Path, data: Any) -> int:
        """Write data as compressed JSONL. Returns token count."""
        tokens = 0
        if self.config.index_format == "jsonl":
            with gzip.open(path, "wt", encoding="utf-8") as f:
                if isinstance(data, list):
                    for item in data:
                        line = json.dumps(item, sort_keys=True)
                        f.write(line + "\n")
                        tokens += len(line) // 4
                else:
                    line = json.dumps(data, sort_keys=True)
                    f.write(line + "\n")
                    tokens += len(line) // 4
        else:
            with gzip.open(path, "wt", encoding="utf-8") as f:
                content = json.dumps(data, sort_keys=True, indent=2)
                f.write(content)
                tokens += len(content) // 4
        return tokens

    def offload(
        self,
        data: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> OffloadReference:
        """Offload context segment to filesystem."""
        meta = OffloadMetadata(**(metadata or {}))
        
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        data_hash = self._compute_hash(data)[:8]
        filename = f"{meta.type}_{meta.range}_{timestamp}_{data_hash}.jsonl.gz"
        filepath = self.base_path / filename
        
        # Write compressed data
        tokens = self._write_compressed(filepath, data)
        
        # Compute hash for verification
        sha256 = self._compute_hash(data)
        
        # Create reference
        ref = OffloadReference(
            path=str(filepath),
            url=f"file://{filepath.absolute()}",
            tokens=tokens,
            metadata=meta,
            sha256=sha256,
        )
        
        # Update index
        index_entry = {
            "path": str(filepath),
            "url": ref.url,
            "tokens": tokens,
            "sha256": sha256,
            "metadata": asdict(meta),
        }
        with open(self.index_path, "a") as f:
            f.write(json.dumps(index_entry) + "\n")
        
        return ref

    def restore(self, path: str) -> Any:
        """Restore data from offload file."""
        filepath = Path(path)
        if not filepath.exists():
            raise FileNotFoundError(f"Offload file not found: {path}")
        
        with gzip.open(filepath, "rt", encoding="utf-8") as f:
            if self.config.index_format == "jsonl":
                data = []
                for line in f:
                    line = line.strip()
                    if line:
                        data.append(json.loads(line))
                return data
            else:
                return json.load(f)

    def restore_by_reference(self, ref: OffloadReference) -> Any:
        """Restore using offload reference with verification."""
        data = self.restore(ref.path)
        # Verify integrity
        actual_hash = self._compute_hash(data)
        if actual_hash != ref.sha256:
            raise ValueError(f"Data integrity check failed: {actual_hash} != {ref.sha256}")
        return data

    def list_offloads(self, type_filter: Optional[str] = None) -> List[OffloadReference]:
        """List all offloaded segments."""
        if not self.index_path.exists():
            return []
        
        refs = []
        with open(self.index_path) as f:
            for line in f:
                entry = json.loads(line.strip())
                meta = OffloadMetadata(**entry["metadata"])
                if type_filter and meta.type != type_filter:
                    continue
                refs.append(OffloadReference(
                    path=entry["path"],
                    url=entry["url"],
                    tokens=entry["tokens"],
                    metadata=meta,
                    sha256=entry["sha256"],
                ))
        return refs

    def get_total_tokens(self) -> int:
        """Get total tokens across all offloads."""
        return sum(r.tokens for r in self.list_offloads())

    def cleanup_old(self, keep_recent: int = 100) -> int:
        """Remove old offload files, keeping only recent N."""
        refs = self.list_offloads()
        if len(refs) <= keep_recent:
            return 0
        
        # Sort by timestamp (from filename)
        refs.sort(key=lambda r: r.metadata.timestamp, reverse=True)
        to_remove = refs[keep_recent:]
        
        removed = 0
        for ref in to_remove:
            try:
                Path(ref.path).unlink()
                removed += 1
            except OSError:
                pass
        
        # Rebuild index
        remaining = refs[:keep_recent]
        with open(self.index_path, "w") as f:
            for ref in remaining:
                f.write(json.dumps({
                    "path": ref.path,
                    "url": ref.url,
                    "tokens": ref.tokens,
                    "sha256": ref.sha256,
                    "metadata": asdict(ref.metadata),
                }) + "\n")
        
        return removed


def main():
    import argparse
    parser = argparse.ArgumentParser(description="File Offloader CLI")
    parser.add_argument("--config", default=".agent_context_config.json")
    parser.add_argument("--data", help="Input data JSON file to offload")
    parser.add_argument("--output", help="Output reference JSON file")
    parser.add_argument("--metadata", help="Metadata JSON file")
    parser.add_argument("--restore", action="store_true", help="Restore from offload")
    parser.add_argument("--path", help="Offload file path to restore")
    parser.add_argument("--list", action="store_true", help="List all offloads")
    parser.add_argument("--cleanup", type=int, help="Cleanup old offloads, keep N recent")
    args = parser.parse_args()

    offloader = FileOffloader.from_config(args.config)

    if args.restore:
        if not args.path:
            parser.error("--path required for restore")
        data = offloader.restore(args.path)
        if args.output:
            with open(args.output, "w") as f:
                json.dump(data, f, indent=2)
        else:
            print(json.dumps(data, indent=2))
    elif args.list:
        refs = offloader.list_offloads()
        for ref in refs:
            print(f"{ref.path} | {ref.tokens} tokens | {ref.metadata.type} | {ref.metadata.timestamp}")
    elif args.cleanup:
        removed = offloader.cleanup_old(args.cleanup)
        print(f"Removed {removed} old offload files")
    else:
        if not args.data:
            parser.error("--data required for offload")
        with open(args.data) as f:
            data = json.load(f)
        
        metadata = {}
        if args.metadata:
            with open(args.metadata) as f:
                metadata = json.load(f)
        
        ref = offloader.offload(data, metadata)
        
        if args.output:
            with open(args.output, "w") as f:
                json.dump(asdict(ref), f, indent=2)
        else:
            print(json.dumps(asdict(ref), indent=2))
        print(f"Offloaded to: {ref.path} ({ref.tokens} tokens)")


if __name__ == "__main__":
    main()
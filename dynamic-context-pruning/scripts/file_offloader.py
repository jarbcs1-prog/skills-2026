from typing import Dict, Any
import os
import json
import gzip

class FileOffloader:
    def __init__(self, base_path: str, compression: str, index_format: str):
        self.base_path = base_path
        self.compression = compression
        self.index_format = index_format
        os.makedirs(self.base_path, exist_ok=True)

    def offload(self, data: Any, metadata: Dict[str, Any]) -> Dict[str, Any]:
        file_name = f"{metadata.get("type", "context")}_{metadata.get("range", "all")}.{self.index_format}"
        file_path = os.path.join(self.base_path, file_name)

        if self.compression == "gzip":
            file_path += ".gz"
            with gzip.open(file_path, "wt", encoding="utf-8") as f:
                json.dump(data, f)
        else:
            with open(file_path, "w") as f:
                json.dump(data, f)

        # Simulate token count
        tokens = len(str(data)) // 4 # rough estimate

        return {"path": file_path, "url": f"file://{file_path}", "tokens": tokens}

    def restore(self, file_path: str) -> Any:
        if file_path.endswith(".gz"):
            with gzip.open(file_path, "rt", encoding="utf-8") as f:
                data = json.load(f)
        else:
            with open(file_path, "r") as f:
                data = json.load(f)
        return data

    @classmethod
    def from_config(cls, config_path: str):
        import json
        with open(config_path, "r") as f:
            config = json.load(f)
        offloading_config = config.get("offloading", {})
        return cls(
            base_path=offloading_config.get("base_path"),
            compression=offloading_config.get("compression"),
            index_format=offloading_config.get("index_format"),
        )

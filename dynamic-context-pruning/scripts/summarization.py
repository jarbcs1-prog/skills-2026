from typing import List, Dict, Any

class SummarySchema:
    def __init__(self, fields: List[str], required: List[str]):
        self.fields = fields
        self.required = required

class Summarizer:
    def __init__(self, schema: SummarySchema, keep_recent_full: int, model: str):
        self.schema = schema
        self.keep_recent_full = keep_recent_full
        self.model = model

    def summarize(self, context_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        # Simulate summarization based on the schema
        summary = {}
        for field in self.schema.fields:
            summary[field] = f"Summary for {field} based on context..."
        return summary

    def validate(self, summary: Dict[str, Any], context_history: List[Dict[str, Any]]) -> bool:
        # Simulate validation
        for field in self.schema.required:
            if field not in summary or not summary[field]:
                return False
        return True

    @classmethod
    def from_config(cls, config_path: str):
        import json
        with open(config_path, 'r') as f:
            config = json.load(f)
        summarization_config = config.get("summarization", {})
        schema_config = summarization_config.get("schema", {})
        schema = SummarySchema(
            fields=schema_config.get("fields", []),
            required=schema_config.get("required", []),
        )
        return cls(
            schema=schema,
            keep_recent_full=summarization_config.get("keep_recent_full"),
            model=summarization_config.get("model"),
        )

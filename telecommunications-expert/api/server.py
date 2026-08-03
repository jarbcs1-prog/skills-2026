"""REST API for the telecom expert (FastAPI + uvicorn, optional dependencies)."""

from __future__ import annotations

from datetime import datetime


def build_app():
    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise ImportError("fastapi is required: pip install fastapi") from exc

    app = FastAPI(title="Telecom Expert API", version="1.0.0")

    @app.get("/health")
    def health() -> dict:
        return {"status": "ok", "time": datetime.utcnow().isoformat()}

    @app.get("/nms/elements")
    def list_elements() -> dict:
        return {"elements": []}

    @app.get("/billing/invoice/{subscriber_id}")
    def invoice(subscriber_id: str) -> dict:
        return {"subscriber_id": subscriber_id, "error": "no billing context loaded"}

    @app.get("/fiveg/slices")
    def list_slices() -> dict:
        return {"slices": []}

    return app


def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    try:
        import uvicorn
    except ImportError as exc:
        raise ImportError("uvicorn is required: pip install uvicorn") from exc
    uvicorn.run(build_app(), host=host, port=port)

"""5G handover management: decide when a UE should move between cells."""

from __future__ import annotations

import random
from typing import Optional


class HandoverManager:
    """Manages inter-cell handovers based on measured RSRP."""

    def __init__(self, threshold_db: float = 3.0, seed: Optional[int] = None) -> None:
        self.threshold_db = threshold_db
        self._rng = random.Random(seed)

    def manage_handover(self, ue_id: str, source_cell: str, target_cell: str) -> dict:
        source_rsrp = self._measure_rsrp(ue_id, source_cell)
        target_rsrp = self._measure_rsrp(ue_id, target_cell)
        if target_rsrp > source_rsrp + self.threshold_db:
            executed = self._execute_handover(ue_id, source_cell, target_cell)
            return {
                "ue_id": ue_id,
                "handover": "executed" if executed else "failed",
                "source_cell": source_cell,
                "target_cell": target_cell,
                "source_rsrp": source_rsrp,
                "target_rsrp": target_rsrp,
            }
        return {
            "ue_id": ue_id,
            "handover": "not_required",
            "source_rsrp": source_rsrp,
            "target_rsrp": target_rsrp,
        }

    def _measure_rsrp(self, ue_id: str, cell_id: str) -> float:
        return self._rng.uniform(-110, -70)

    def _execute_handover(self, ue_id: str, source: str, target: str) -> bool:
        return True

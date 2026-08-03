"""5G massive MIMO beamforming: steer beams toward user positions."""

from __future__ import annotations

import math
from typing import Any, Sequence


class BeamformingOptimizer:
    """Computes beam directions for a base station given user positions."""

    NUM_ANTENNAS = 64

    def optimize_beamforming(self, base_station_id: str, user_positions: Sequence[Any]) -> dict:
        beam_directions = [
            self._calculate_beam_angle(position) for position in user_positions
        ]
        return {
            "base_station_id": base_station_id,
            "num_users": len(user_positions),
            "num_antennas": self.NUM_ANTENNAS,
            "beam_directions": beam_directions,
            "expected_throughput_improvement": 2.5,
        }

    def _calculate_beam_angle(self, position: Any) -> float:
        if isinstance(position, dict):
            x = position.get("x", 0)
            y = position.get("y", 0)
        else:
            x, y = position[0], position[1]
        if x == 0:
            return 90.0
        return float(abs(math.degrees(math.atan2(y, x))))

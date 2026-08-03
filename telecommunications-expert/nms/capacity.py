"""Capacity planning: predict when a region's network exhausts its capacity."""

from __future__ import annotations

import math
from typing import Dict

from core.models import NetworkElement


def predict_capacity_exhaustion(
    total_capacity: float, current_usage: float, growth_rate: float = 0.15
) -> float:
    """Months until utilization reaches 90% of total capacity (0 = now, inf = never)."""
    if current_usage >= total_capacity:
        return 0.0
    target = total_capacity * 0.9
    usage_needed = target - current_usage
    if usage_needed <= 0:
        return 0.0
    monthly_growth = growth_rate / 12
    if current_usage <= 0 or monthly_growth <= 0:
        return float("inf")
    return math.log(1 + usage_needed / current_usage) / math.log(1 + monthly_growth)


def analyze_network_capacity(network_elements: Dict[str, NetworkElement], region: str) -> dict:
    """Aggregate capacity across a region and forecast exhaustion."""
    region_elements = [
        element
        for element in network_elements.values()
        if element.location.get("region") == region
    ]
    if not region_elements:
        return {"error": "No network elements in region"}
    total_capacity = sum(
        element.capacity.get("bandwidth_gbps", 0) for element in region_elements
    )
    total_used = sum(
        element.capacity.get("bandwidth_gbps", 0)
        * (element.utilization.get("bandwidth_percent", 0) / 100)
        for element in region_elements
    )
    utilization_percent = (total_used / total_capacity * 100) if total_capacity > 0 else 0
    months = predict_capacity_exhaustion(total_capacity, total_used)
    return {
        "region": region,
        "total_capacity_gbps": total_capacity,
        "used_capacity_gbps": total_used,
        "available_capacity_gbps": total_capacity - total_used,
        "utilization_percent": utilization_percent,
        "predicted_full_in_months": months,
        "expansion_recommended": months < 12,
    }

"""Demonstration-only decision policy. Never an automated real credit decision."""
from __future__ import annotations

from ..config import load_config
from ..models.registry import load_json


def get_thresholds() -> dict:
    cfg = load_config("thresholds")
    try:
        t = load_json("thresholds.json")  # validation-selected
        return {"medium": t["medium"], "high": t["high"]}
    except FileNotFoundError:
        return {"medium": cfg["medium"], "high": cfg["high"]}


def tier_for(score: float, thresholds: dict | None = None) -> str:
    t = thresholds or get_thresholds()
    if score >= t["high"]:
        return "High"
    if score >= t["medium"]:
        return "Medium"
    return "Low"


def recommendation_for(tier: str) -> str:
    return load_config("thresholds")["recommendations"][tier]


def display_score(score: float) -> int:
    return int(round(max(0.0, min(1.0, float(score))) * 100))

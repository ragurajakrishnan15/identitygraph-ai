from __future__ import annotations

from pydantic import BaseModel, Field

from .application import ApplicationIn


class Factor(BaseModel):
    feature: str
    description: str
    contribution: float
    direction: str


class ScoreResponse(BaseModel):
    application_id: str
    score: float = Field(description="Uncalibrated model score in [0,1]; NOT a probability")
    display_score: int = Field(ge=0, le=100)
    tier: str
    recommendation: str
    model_version: str
    scored_at: str
    top_factors: list[Factor]
    linked_entities: list[dict]
    is_simulated: bool = True
    note: str = "Simulated demonstration output; not a real credit decision."


class BatchScoreRequest(BaseModel):
    applications: list[ApplicationIn] = Field(min_length=1, max_length=100)

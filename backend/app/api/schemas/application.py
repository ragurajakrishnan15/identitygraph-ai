from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ApplicationIn(BaseModel):
    """Online scoring request. Labels are rejected (extra='forbid')."""

    model_config = ConfigDict(extra="forbid")
    application_id: str | None = None
    applicant_id: str | None = None
    application_timestamp: datetime | None = None
    full_name: str = Field(min_length=1)
    date_of_birth: str = Field(pattern=r"^\d{4}-\d{2}-\d{2}$")
    email: str = Field(pattern=r"^[^@\s]+@[^@\s]+$")
    phone: str = Field(min_length=5)
    address: str = Field(min_length=3)
    device_id: str = Field(min_length=1)
    ip_address: str = Field(pattern=r"^\d{1,3}(\.\d{1,3}){3}$")
    employment_status: Literal["employed", "self_employed", "unemployed", "student", "retired"]
    annual_income: float = Field(gt=0)
    requested_credit: float = Field(gt=0)
    application_channel: Literal["web", "mobile", "branch", "partner"]


class NoteIn(BaseModel):
    note: str = Field(min_length=1, max_length=2000)

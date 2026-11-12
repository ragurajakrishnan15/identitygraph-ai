from __future__ import annotations

from sqlalchemy import JSON, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .session import Base


class ApplicationRow(Base):
    __tablename__ = "applications"
    application_id: Mapped[str] = mapped_column(String, primary_key=True)
    applicant_id: Mapped[str] = mapped_column(String, index=True)
    application_timestamp: Mapped[str] = mapped_column(String, index=True)
    full_name: Mapped[str] = mapped_column(String)
    date_of_birth: Mapped[str] = mapped_column(String)
    email: Mapped[str] = mapped_column(String, index=True)
    phone: Mapped[str] = mapped_column(String, index=True)
    address: Mapped[str] = mapped_column(String)
    device_id: Mapped[str] = mapped_column(String, index=True)
    ip_address: Mapped[str] = mapped_column(String)
    employment_status: Mapped[str] = mapped_column(String)
    annual_income: Mapped[float] = mapped_column(Float)
    requested_credit: Mapped[float] = mapped_column(Float)
    application_channel: Mapped[str] = mapped_column(String, index=True)
    fraud_label: Mapped[int | None] = mapped_column(Integer, nullable=True)  # training-only / synthetic
    fraud_scenario: Mapped[str | None] = mapped_column(String, nullable=True)
    source: Mapped[str] = mapped_column(String, default="synthetic")  # synthetic | online
    split: Mapped[str | None] = mapped_column(String, nullable=True)


class ScoreRow(Base):
    __tablename__ = "scores"
    application_id: Mapped[str] = mapped_column(String, primary_key=True)
    score: Mapped[float] = mapped_column(Float, index=True)
    display_score: Mapped[int] = mapped_column(Integer)
    tier: Mapped[str] = mapped_column(String, index=True)
    recommendation: Mapped[str] = mapped_column(String)
    model_version: Mapped[str] = mapped_column(String)
    scored_at: Mapped[str] = mapped_column(String)
    factors: Mapped[list] = mapped_column(JSON)


class EntityRow(Base):
    __tablename__ = "entities"
    entity_id: Mapped[str] = mapped_column(String, primary_key=True)
    kind: Mapped[str] = mapped_column(String, index=True)
    label: Mapped[str] = mapped_column(String)
    degree: Mapped[int] = mapped_column(Integer)


class EntityEdgeRow(Base):
    __tablename__ = "entity_edges"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source: Mapped[str] = mapped_column(String, index=True)
    target: Mapped[str] = mapped_column(String, index=True)
    relation: Mapped[str] = mapped_column(String)


class ModelVersionRow(Base):
    __tablename__ = "model_versions"
    version: Mapped[str] = mapped_column(String, primary_key=True)
    model_name: Mapped[str] = mapped_column(String)
    trained_at: Mapped[str] = mapped_column(String)
    metrics: Mapped[dict] = mapped_column(JSON)


class MonitoringSnapshotRow(Base):
    __tablename__ = "monitoring_snapshots"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    generated_at: Mapped[str] = mapped_column(String)
    payload: Mapped[dict] = mapped_column(JSON)


class InvestigationNoteRow(Base):
    __tablename__ = "investigation_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    application_id: Mapped[str] = mapped_column(String, index=True)
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String)

from __future__ import annotations

from sqlalchemy import func, or_, select

from .models import (
    ApplicationRow,
    InvestigationNoteRow,
    ModelVersionRow,
    MonitoringSnapshotRow,
    ScoreRow,
)
from .session import get_session

SORTS = {
    "score": ScoreRow.score, "timestamp": ApplicationRow.application_timestamp,
    "income": ApplicationRow.annual_income, "credit": ApplicationRow.requested_credit,
}


def _app_dict(a: ApplicationRow, s: ScoreRow | None) -> dict:
    d = {c.name: getattr(a, c.name) for c in a.__table__.columns}
    d["score"] = None
    if s:
        d["score"] = {c.name: getattr(s, c.name) for c in s.__table__.columns}
    return d


class ApplicationRepository:
    def list(self, q=None, tier=None, channel=None, sort="timestamp", order="desc", page=1, page_size=25):
        with get_session() as db:
            stmt = select(ApplicationRow, ScoreRow).join(ScoreRow, ScoreRow.application_id == ApplicationRow.application_id, isouter=True)
            if q:
                like = f"%{q}%"
                stmt = stmt.where(or_(ApplicationRow.application_id.ilike(like), ApplicationRow.full_name.ilike(like),
                                      ApplicationRow.email.ilike(like), ApplicationRow.device_id.ilike(like),
                                      ApplicationRow.phone.ilike(like)))
            if tier:
                stmt = stmt.where(ScoreRow.tier == tier)
            if channel:
                stmt = stmt.where(ApplicationRow.application_channel == channel)
            total = db.scalar(select(func.count()).select_from(stmt.subquery()))
            col = SORTS.get(sort, ApplicationRow.application_timestamp)
            stmt = stmt.order_by(col.desc() if order == "desc" else col.asc())
            rows = db.execute(stmt.offset((page - 1) * page_size).limit(page_size)).all()
            return [_app_dict(a, s) for a, s in rows], total

    def get(self, application_id: str):
        with get_session() as db:
            a = db.get(ApplicationRow, application_id)
            if not a:
                return None
            return _app_dict(a, db.get(ScoreRow, application_id))

    def all_frame(self):
        import pandas as pd
        with get_session() as db:
            rows = db.execute(select(ApplicationRow)).scalars().all()
            return pd.DataFrame([{c.name: getattr(r, c.name) for c in r.__table__.columns} for r in rows])

    def save_online(self, app: dict, score: dict):
        with get_session() as db:
            db.merge(ApplicationRow(**app))
            db.merge(ScoreRow(**score))
            db.commit()

    def overview(self) -> dict:
        with get_session() as db:
            total = db.scalar(select(func.count(ApplicationRow.application_id)))
            tiers = dict(db.execute(select(ScoreRow.tier, func.count()).group_by(ScoreRow.tier)).all())
            ch = db.execute(select(ApplicationRow.application_channel, ScoreRow.tier, func.count())
                            .join(ScoreRow, ScoreRow.application_id == ApplicationRow.application_id)
                            .group_by(ApplicationRow.application_channel, ScoreRow.tier)).all()
            avg = db.scalar(select(func.avg(ScoreRow.score)))
            trend = db.execute(
                select(func.substr(ApplicationRow.application_timestamp, 1, 7), func.count(), func.avg(ScoreRow.score))
                .join(ScoreRow, ScoreRow.application_id == ApplicationRow.application_id)
                .group_by(func.substr(ApplicationRow.application_timestamp, 1, 7))
                .order_by(func.substr(ApplicationRow.application_timestamp, 1, 7))).all()
            return {"total": total, "tiers": tiers, "avg_score": avg or 0,
                    "channels": [{"channel": c, "tier": t, "count": n} for c, t, n in ch],
                    "trend": [{"period": p, "applications": n, "avg_score": a} for p, n, a in trend]}


class ModelRepository:
    def list(self):
        with get_session() as db:
            return [{"version": m.version, "model_name": m.model_name, "trained_at": m.trained_at, "metrics": m.metrics}
                    for m in db.execute(select(ModelVersionRow).order_by(ModelVersionRow.trained_at.desc())).scalars()]


class MonitoringRepository:
    def latest(self):
        with get_session() as db:
            r = db.execute(select(MonitoringSnapshotRow).order_by(MonitoringSnapshotRow.id.desc())).scalars().first()
            return r.payload if r else None


class NoteRepository:
    def add(self, application_id: str, note: str, created_at: str):
        with get_session() as db:
            db.add(InvestigationNoteRow(application_id=application_id, note=note, created_at=created_at))
            db.commit()

    def list(self, application_id: str):
        with get_session() as db:
            rows = db.execute(select(InvestigationNoteRow).where(InvestigationNoteRow.application_id == application_id)
                              .order_by(InvestigationNoteRow.id.desc())).scalars()
            return [{"id": n.id, "note": n.note, "created_at": n.created_at} for n in rows]

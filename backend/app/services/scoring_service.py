from __future__ import annotations

import logging
import threading
import uuid
from datetime import datetime, timezone

import pandas as pd

from identitygraph.decisioning.policy import display_score, recommendation_for, tier_for
from identitygraph.explainability.explanations import explain_rows
from identitygraph.features.online import OnlineFallback, OnlineFeaturizer
from identitygraph.models.predict import score_frame, score_new_applications, score_new_applications_online

from ..db.repositories import ApplicationRepository
from . import graph_service
from .model_service import get_bundle

repo = ApplicationRepository()
_lock = threading.Lock()
_history: pd.DataFrame | None = None
_featurizer: OnlineFeaturizer | None = None
log = logging.getLogger("identitygraph")


def _get_history() -> pd.DataFrame:
    """In-memory history (loaded once, extended with online applications)."""
    global _history
    if _history is None:
        h = repo.all_frame()
        h["application_timestamp"] = pd.to_datetime(h["application_timestamp"])
        _history = h.sort_values("application_timestamp").reset_index(drop=True)
    return _history


def _get_featurizer() -> OnlineFeaturizer:
    global _featurizer
    if _featurizer is None:
        _featurizer = OnlineFeaturizer(_get_history())
    return _featurizer


def reset_cache():
    global _history, _featurizer
    _history = None
    _featurizer = None


def warm_up() -> None:
    """Build the in-memory history/featurizer and initialise SHAP so the first real request is fast.
    Safe to run in a background thread; never raises."""
    global _featurizer
    try:
        with _lock:
            history = _get_history()
            fz = _get_featurizer()
            probe = history.iloc[[-1]][RAW].copy()
            probe["application_id"] = "WARMUP"
            feats = fz.features(probe, commit=False)
            feats["score"] = score_frame(get_bundle(), feats)
            explain_rows(get_bundle(), feats)
        log.info("scoring warm-up complete (%d history rows)", len(history))
    except Exception:  # noqa: BLE001
        _featurizer = None
        log.exception("scoring warm-up failed (scoring still works, first call will be slower)")
RAW = ["application_id", "applicant_id", "application_timestamp", "full_name", "date_of_birth", "email", "phone",
       "address", "device_id", "ip_address", "employment_status", "annual_income", "requested_credit",
       "application_channel"]


def _prepare(payloads: list[dict]) -> pd.DataFrame:
    rows = []
    for p in payloads:
        p = dict(p)
        p["application_id"] = p.get("application_id") or f"NEW-{uuid.uuid4().hex[:10].upper()}"
        p["applicant_id"] = p.get("applicant_id") or f"APL-{uuid.uuid4().hex[:8].upper()}"
        ts = pd.Timestamp(p.get("application_timestamp") or datetime.now(timezone.utc))
        p["application_timestamp"] = ts.tz_localize(None) if ts.tzinfo is None else ts.tz_convert("UTC").tz_localize(None)
        rows.append({k: p[k] for k in RAW})
    return pd.DataFrame(rows)


def _featurise_and_score(bundle: dict, history: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Incremental features when possible; otherwise the full point-in-time recompute."""
    global _featurizer
    try:
        return score_new_applications_online(bundle, _get_featurizer(), new)
    except OnlineFallback:
        _featurizer = None  # history is about to change underneath it; rebuild lazily
        return score_new_applications(bundle, history, new)
    except Exception:
        _featurizer = None  # state may hold rows that never got stored
        raise


def _py(v):
    return v.item() if hasattr(v, "item") else v


def _score_locked(bundle: dict, history: pd.DataFrame, new: pd.DataFrame) -> list[dict]:
    global _featurizer
    try:
        feats = _featurise_and_score(bundle, history, new)
        factors = explain_rows(bundle, feats)
        now = datetime.now(timezone.utc).isoformat()
        out = []
        for (_, row), f in zip(feats.iterrows(), factors, strict=True):
            tier = tier_for(float(row["score"]), bundle["thresholds"])
            rec = {
                "application_id": row["application_id"], "score": float(row["score"]),
                "display_score": display_score(row["score"]), "tier": tier,
                "recommendation": recommendation_for(tier), "model_version": bundle["version"],
                "scored_at": now, "factors": f,
            }
            app = {k: _py(row[k]) for k in RAW}
            app["application_timestamp"] = pd.Timestamp(app["application_timestamp"]).isoformat()
            app.update(source="online", fraud_label=None, fraud_scenario=None, split=None)
            repo.save_online(app, rec)
            out.append(rec)
        _extend_history(new)
        graph_service.add_rows(new)
        return out
    except Exception:
        _featurizer = None  # cached state may include rows that were never stored
        raise


def score_payloads(payloads: list[dict]) -> list[dict]:
    bundle = get_bundle()
    new = _prepare(payloads)
    with _lock:
        history = _get_history()
        dup = set(new["application_id"]) & set(history["application_id"])
        if dup:
            raise ValueError(f"application_id already exists: {sorted(dup)[:3]}")
        out = _score_locked(bundle, history, new)
    return [_response(r) for r in out]


def _extend_history(new: pd.DataFrame) -> None:
    global _history
    add = new.copy()
    add["fraud_label"] = float("nan")  # unknown label: ignored by neighbor_fraud_ratio at any age
    _history = pd.concat([_get_history(), add], ignore_index=True)


def _response(rec: dict) -> dict:
    return {
        "application_id": rec["application_id"], "score": rec["score"], "display_score": rec["display_score"],
        "tier": rec["tier"], "recommendation": rec["recommendation"], "model_version": rec["model_version"],
        "scored_at": rec["scored_at"], "top_factors": rec["factors"],
        "linked_entities": graph_service.links_for_application(rec["application_id"]),
        "is_simulated": True,
    }


def stored_score(application_id: str) -> dict | None:
    a = repo.get(application_id)
    if not a or not a["score"]:
        return None
    return _response(a["score"])

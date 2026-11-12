"""Seed the database from generated data + trained artifacts (no values are invented)."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd
from sqlalchemy import delete

from identitygraph.config import PROCESSED_DIR
from identitygraph.decisioning.policy import display_score, recommendation_for, tier_for
from identitygraph.explainability.explanations import explain_rows
from identitygraph.graph.builder import build_graph
from identitygraph.models.predict import score_frame
from identitygraph.models.registry import load_bundle, load_json

from .models import (
    ApplicationRow,
    EntityEdgeRow,
    EntityRow,
    ModelVersionRow,
    MonitoringSnapshotRow,
    ScoreRow,
)
from .session import get_engine, get_session, init_db

APP_COLS = ["application_id", "applicant_id", "application_timestamp", "full_name", "date_of_birth", "email",
            "phone", "address", "device_id", "ip_address", "employment_status", "annual_income",
            "requested_credit", "application_channel", "fraud_label", "fraud_scenario", "split"]


def seed(limit: int | None = None) -> dict:
    init_db()
    bundle = load_bundle()
    feats = pd.read_parquet(PROCESSED_DIR / "features.parquet")
    if limit:
        feats = feats.tail(limit).reset_index(drop=True)
    scores = score_frame(bundle, feats)
    now = datetime.now(timezone.utc).isoformat()
    factors = []
    for i in range(0, len(feats), 2000):
        factors += explain_rows(bundle, feats.iloc[i:i + 2000])
    thr = bundle["thresholds"]
    with get_session() as db:
        for t in (ScoreRow, ApplicationRow, EntityEdgeRow, EntityRow, ModelVersionRow, MonitoringSnapshotRow):
            db.execute(delete(t))
        apps, srows = [], []
        for rec, s, f in zip(feats[APP_COLS].to_dict("records"), scores, factors, strict=True):
            rec["application_timestamp"] = pd.Timestamp(rec["application_timestamp"]).isoformat()
            rec["fraud_label"] = int(rec["fraud_label"])
            apps.append(ApplicationRow(**rec, source="synthetic"))
            tier = tier_for(float(s), thr)
            srows.append(ScoreRow(application_id=rec["application_id"], score=float(s),
                                  display_score=display_score(s), tier=tier,
                                  recommendation=recommendation_for(tier), model_version=bundle["version"],
                                  scored_at=now, factors=f))
        db.bulk_save_objects(apps)
        db.bulk_save_objects(srows)
        g = build_graph(feats)
        db.bulk_save_objects([EntityRow(entity_id=n, kind=d["kind"], label=d["label"], degree=g.degree(n))
                              for n, d in g.nodes(data=True) if d["kind"] not in ("application", "applicant")])
        db.bulk_save_objects([EntityEdgeRow(source=a, target=b, relation=d.get("relation", ""))
                              for a, b, d in g.edges(data=True)])
        metrics = load_json("metrics.json")
        db.add(ModelVersionRow(version=metrics["version"], model_name=metrics["primary_model"],
                               trained_at=metrics["trained_at"], metrics=metrics))
        try:
            snap = load_json("monitoring.json")
            db.add(MonitoringSnapshotRow(generated_at=snap["generated_at"], payload=snap))
        except FileNotFoundError:
            pass
        db.commit()
    get_engine()
    return {"applications": len(feats), "nodes": g.number_of_nodes(), "edges": g.number_of_edges()}

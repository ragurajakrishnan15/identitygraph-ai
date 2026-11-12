"""Build a monitoring snapshot: reference = train period, current = held-out test period."""
from __future__ import annotations

from datetime import datetime, timezone

import pandas as pd

from ..data.schemas import APPLICATION_COLUMNS
from ..features.pipeline import BASE_FEATURES, GRAPH_FEATURES
from ..models.predict import score_frame
from .data_quality import quality_report
from .drift import feature_drift
from .prediction_stats import score_distribution, tier_distribution


def build_snapshot(bundle: dict, features: pd.DataFrame) -> dict:
    ref = features[features["split"] == "train"]
    cur = features[features["split"] == "test"]
    s_ref, s_cur = score_frame(bundle, ref), score_frame(bundle, cur)
    from .drift import psi, status_for

    sp = psi(pd.Series(s_ref), pd.Series(s_cur))
    snap = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "batch (train period vs held-out test period); not real-time",
        "model_version": bundle["version"],
        "quality": quality_report(cur[[c for c in APPLICATION_COLUMNS]]),
        "feature_drift": feature_drift(ref, cur, BASE_FEATURES + GRAPH_FEATURES),
        "score_psi": {"psi": sp, "status": status_for(sp)},
        "score_distribution": score_distribution(s_cur),
        "tier_distribution": tier_distribution(s_cur, bundle["thresholds"]),
        "label_performance": {
            "available": True,
            "note": "Labels in this synthetic set are fully matured. In production, only compute once labels mature.",
            "pr_auc_test": None,
        },
    }
    from sklearn.metrics import average_precision_score
    snap["label_performance"]["pr_auc_test"] = float(average_precision_score(cur["fraud_label"], s_cur))
    return snap

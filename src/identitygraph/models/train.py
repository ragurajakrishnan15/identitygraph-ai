from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from .. import __version__
from ..config import PROCESSED_DIR, load_config
from ..evaluation.metrics import compute_metrics, curves
from ..evaluation.splits import chronological_split
from ..features.pipeline import build_features
from .baseline import build_pipeline, model_specs
from .registry import save_bundle, save_json
from .thresholds import select_thresholds


def _importance(pipe, feats: list[str]) -> list[dict]:
    clf = pipe.named_steps["clf"]
    names = list(pipe.named_steps["prep"].get_feature_names_out())
    if hasattr(clf, "feature_importances_"):
        vals = clf.feature_importances_
    else:
        vals = np.abs(clf.coef_[0])
        vals = vals / max(vals.sum(), 1e-12)
    clean = [n.split("__", 1)[-1] for n in names]
    order = np.argsort(-vals)[:20]
    return [{"feature": clean[i], "importance": float(vals[i])} for i in order]


def train_all(df_raw: pd.DataFrame, out_dir: Path | None = None, save_features: bool = True) -> dict:
    mcfg = load_config("model")
    rs = mcfg["random_state"]
    train_raw, val_raw, test_raw, train_end = chronological_split(
        df_raw, mcfg["split"]["train_frac"], mcfg["split"]["val_frac"])
    feats_df = build_features(df_raw, train_end=train_end)
    n_tr, n_va = len(train_raw), len(val_raw)
    tr, va, te = feats_df.iloc[:n_tr], feats_df.iloc[n_tr:n_tr + n_va], feats_df.iloc[n_tr + n_va:]
    if save_features:
        PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
        feats_df.assign(split=["train"] * n_tr + ["val"] * n_va + ["test"] * len(te)).to_parquet(
            PROCESSED_DIR / "features.parquet", index=False)

    results, fitted = {}, {}
    for name in model_specs(rs):
        pipe, feats = build_pipeline(name, rs)
        cols = feats + ["employment_status", "application_channel"]
        pipe.fit(tr[cols], tr["fraud_label"])  # preprocessing is fit on TRAIN only
        s_val = pipe.predict_proba(va[cols])[:, 1]
        thr = select_thresholds(va["fraud_label"], s_val)  # thresholds from VALIDATION only
        s_te = pipe.predict_proba(te[cols])[:, 1]
        results[name] = {
            "validation": compute_metrics(va["fraud_label"], s_val, thr["high"]),
            "test": compute_metrics(te["fraud_label"], s_te, thr["high"]),
            "thresholds": thr, "curves_test": curves(te["fraud_label"], s_te),
            "feature_importance": _importance(pipe, feats), "n_features": len(feats),
        }
        fitted[name] = (pipe, feats, thr)

    primary = mcfg["primary_model"]
    pipe, feats, thr = fitted[primary]
    version = f"{__version__}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M')}"
    bundle = {
        "pipeline": pipe, "features": feats + ["employment_status", "application_channel"],
        "model_name": primary, "version": version, "thresholds": thr,
        "train_end": train_end, "trained_at": datetime.now(timezone.utc).isoformat(),
        "calibrated": False,
    }
    report = {
        "version": version, "primary_model": primary, "trained_at": bundle["trained_at"],
        "data": {"n_total": len(df_raw), "n_train": n_tr, "n_val": n_va, "n_test": len(te),
                 "train_end": str(train_end), "fraud_rate_test": float(te["fraud_label"].mean()),
                 "synthetic": True},
        "models": results,
        "note": "Synthetic data. Scores are uncalibrated; not probabilities.",
    }
    save_bundle(bundle, (out_dir / "model.joblib") if out_dir else None)
    save_json(report, "metrics.json", out_dir)
    save_json(thr, "thresholds.json", out_dir)
    return report

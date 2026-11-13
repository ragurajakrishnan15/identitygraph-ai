from __future__ import annotations

import numpy as np
import pandas as pd

from ..features.pipeline import build_features


def score_frame(bundle: dict, feats: pd.DataFrame):
    return bundle["pipeline"].predict_proba(feats[bundle["features"]])[:, 1]


def score_new_applications(bundle: dict, history: pd.DataFrame, new: pd.DataFrame) -> pd.DataFrame:
    """Compute point-in-time features for `new` rows appended to `history` and score them.

    `new` must contain no label columns; labels from `history` are only used under the train cutoff
    stored in the model bundle. Returns the featurised new rows with a `score` column.
    """
    new = new.copy()
    for c in ("fraud_label", "fraud_scenario"):
        if c in new.columns:
            new = new.drop(columns=c)
    new["fraud_label"] = np.nan  # unknown label: excluded from neighbor_fraud_ratio at any age
    hist = history[[c for c in new.columns if c in history.columns]].copy()
    allrows = pd.concat([hist, new], ignore_index=True)
    allrows["_is_new"] = [False] * len(hist) + [True] * len(new)
    feats = build_features(allrows.drop(columns="_is_new"), train_end=bundle["train_end"])
    # build_features re-sorts stably by timestamp; recover new rows by application_id
    out = feats[feats["application_id"].isin(new["application_id"])].copy()
    out["score"] = score_frame(bundle, out)
    return out


def score_new_applications_online(bundle: dict, featurizer, new: pd.DataFrame) -> pd.DataFrame:
    """Same result as `score_new_applications`, computed incrementally from cached state (see
    features/online.py). Raises OnlineFallback when the full recompute is required."""
    new = new.drop(columns=[c for c in ("fraud_label", "fraud_scenario") if c in new.columns])
    out = featurizer.features(new)
    out["score"] = score_frame(bundle, out)
    return out

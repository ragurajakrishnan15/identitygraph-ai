from __future__ import annotations

import numpy as np
import pandas as pd


def psi(reference: pd.Series, current: pd.Series, bins: int = 10, eps: float = 1e-4) -> float:
    ref, cur = np.asarray(reference, float), np.asarray(current, float)
    edges = np.unique(np.quantile(ref, np.linspace(0, 1, bins + 1)))
    if len(edges) < 3:
        return 0.0
    edges[0], edges[-1] = -np.inf, np.inf
    r = np.histogram(ref, edges)[0] / len(ref)
    c = np.histogram(cur, edges)[0] / len(cur)
    r, c = np.clip(r, eps, None), np.clip(c, eps, None)
    return float(np.sum((c - r) * np.log(c / r)))


def status_for(v: float) -> str:
    return "stable" if v < 0.1 else "moderate" if v < 0.25 else "significant"


def feature_drift(ref: pd.DataFrame, cur: pd.DataFrame, features: list[str], bins: int = 10) -> list[dict]:
    rows = [{"feature": f, "psi": (v := psi(ref[f], cur[f], bins)), "status": status_for(v)} for f in features]
    return sorted(rows, key=lambda r: -r["psi"])

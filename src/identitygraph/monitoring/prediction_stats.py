from __future__ import annotations

import numpy as np
import pandas as pd

from ..decisioning.policy import tier_for


def score_distribution(scores, bins: int = 20) -> list[dict]:
    h, e = np.histogram(scores, bins=bins, range=(0, 1))
    return [{"bin": f"{e[i]:.2f}-{e[i + 1]:.2f}", "count": int(h[i])} for i in range(bins)]


def tier_distribution(scores, thresholds: dict) -> dict:
    tiers = pd.Series([tier_for(s, thresholds) for s in scores])
    vc = tiers.value_counts()
    return {k: int(vc.get(k, 0)) for k in ("Low", "Medium", "High")}

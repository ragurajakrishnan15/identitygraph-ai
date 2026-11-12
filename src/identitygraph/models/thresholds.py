from __future__ import annotations

import numpy as np
from sklearn.metrics import precision_recall_curve


def select_thresholds(y_val, s_val) -> dict:
    """Select thresholds on VALIDATION only.

    high   = score maximising F1 on validation.
    medium = lowest score that still keeps validation recall >= 0.90 (never above `high`).
    """
    p, r, t = precision_recall_curve(y_val, s_val)
    f1 = 2 * p[:-1] * r[:-1] / np.maximum(p[:-1] + r[:-1], 1e-12)
    high = float(t[int(np.argmax(f1))])
    ok = np.where(r[:-1] >= 0.90)[0]
    medium = float(t[ok[-1]]) if len(ok) else high / 2
    medium = min(medium, high)
    return {"medium": medium, "high": high, "selected_on": "validation"}

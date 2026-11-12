from __future__ import annotations

import numpy as np
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)


def recall_at_fpr(y, s, fpr_target: float = 0.01) -> float:
    fpr, tpr, _ = roc_curve(y, s)
    return float(tpr[fpr <= fpr_target].max()) if (fpr <= fpr_target).any() else 0.0


def precision_at_budget(y, s, budget_frac: float = 0.01) -> float:
    k = max(1, int(len(y) * budget_frac))
    top = np.argsort(-np.asarray(s))[:k]
    return float(np.asarray(y)[top].mean())


def compute_metrics(y, s, threshold: float) -> dict:
    y = np.asarray(y)
    s = np.asarray(s)
    pred = (s >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "pr_auc": float(average_precision_score(y, s)),
        "roc_auc": float(roc_auc_score(y, s)),
        "precision": float(precision_score(y, pred, zero_division=0)),
        "recall": float(recall_score(y, pred, zero_division=0)),
        "f1": float(f1_score(y, pred, zero_division=0)),
        "recall_at_1pct_fpr": recall_at_fpr(y, s),
        "precision_at_1pct_review_budget": precision_at_budget(y, s),
        "threshold": float(threshold),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "n": int(len(y)), "positives": int(y.sum()),
    }


def curves(y, s, points: int = 60) -> dict:
    p, r, _ = precision_recall_curve(y, s)
    fpr, tpr, _ = roc_curve(y, s)

    def thin(a, b):
        idx = np.linspace(0, len(a) - 1, min(points, len(a))).astype(int)
        return [[float(a[i]), float(b[i])] for i in idx]

    return {"pr": thin(r, p), "roc": thin(fpr, tpr)}

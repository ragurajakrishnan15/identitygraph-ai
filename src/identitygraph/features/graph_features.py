"""Leakage-safe graph features computed chronologically with union-find.

component_size / component_distinct_applicants: size of the connected component (over applications
and shared entities) that exists *at the moment* the application arrives, including itself.
max_entity_degree: largest number of prior applications on any of its entities.
neighbor_fraud_ratio: among earlier applications sharing any entity, the share labelled fraud, counting
only labels that are (a) matured (older than maturity_days) and (b) from the train period (<= train_end).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def epoch_seconds(ts: pd.Series) -> np.ndarray:
    """Unit-safe epoch seconds (pandas 3 may store datetimes as s/ms/us/ns)."""
    return ((ts - pd.Timestamp("1970-01-01")) // pd.Timedelta(seconds=1)).to_numpy().astype("int64")


class _DSU:
    def __init__(self):
        self.parent: dict = {}
        self.apps: dict = {}
        self.people: dict = {}

    def find(self, x):
        self.parent.setdefault(x, x)
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return ra
        if self.apps.get(ra, 0) < self.apps.get(rb, 0):
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.apps[ra] = self.apps.get(ra, 0) + self.apps.pop(rb, 0)
        self.people.setdefault(ra, set()).update(self.people.pop(rb, set()))
        return ra


def graph_features(df: pd.DataFrame, entity_cols: list[str], train_end=None,
                   maturity_days: int = 30) -> pd.DataFrame:
    """df must be sorted by application_timestamp ascending."""
    n = len(df)
    dsu = _DSU()
    comp_size = np.zeros(n, dtype=int)
    comp_people = np.zeros(n, dtype=int)
    max_deg = np.zeros(n, dtype=int)
    entity_seen: dict = {}
    cols = [df[c].to_numpy() for c in entity_cols]
    applicants = df["applicant_id"].to_numpy()
    for i in range(n):
        node = ("app", i)
        dsu.parent[node] = node
        dsu.apps[node] = 1
        dsu.people[node] = {applicants[i]}
        deg = 0
        for cname, arr in zip(entity_cols, cols, strict=True):
            key = (cname, arr[i])
            deg = max(deg, entity_seen.get(key, 0))
            entity_seen[key] = entity_seen.get(key, 0) + 1
            dsu.parent.setdefault(key, key)
            dsu.apps.setdefault(key, 0)
            dsu.people.setdefault(key, set())
            dsu.union(node, key)
        root = dsu.find(node)
        comp_size[i] = dsu.apps[root]
        comp_people[i] = len(dsu.people[root])
        max_deg[i] = deg

    # neighbor fraud ratio, per entity, with maturity lag and train cutoff
    ts = epoch_seconds(df["application_timestamp"])
    # Unknown labels (NaN/None, e.g. applications scored online) are excluded from numerator AND denominator.
    labels = (pd.to_numeric(df["fraud_label"], errors="coerce").to_numpy(dtype=float)
              if "fraud_label" in df.columns else np.full(n, np.nan))
    known = ~np.isnan(labels)
    labels = np.where(known, labels, 0.0)
    lag = maturity_days * 86400
    cutoff = ts.max() if train_end is None else int((pd.Timestamp(train_end) - pd.Timestamp('1970-01-01')) // pd.Timedelta(seconds=1))
    fraud_known = np.zeros(n)
    total_known = np.zeros(n)
    for c in entity_cols:
        for _, idx in df.groupby(c).indices.items():
            t = ts[idx]
            lab = labels[idx]
            usable = ((t <= cutoff) & known[idx]).astype(int)  # only known, train-period labels
            cum_n = np.concatenate([[0], np.cumsum(usable)])
            cum_f = np.concatenate([[0], np.cumsum(lab * usable)])
            upto = np.searchsorted(t, t - lag, side="right")  # prior rows old enough to be matured
            upto = np.minimum(upto, np.arange(len(idx)))
            total_known[idx] += cum_n[upto]
            fraud_known[idx] += cum_f[upto]
    ratio = np.where(total_known > 0, fraud_known / np.maximum(total_known, 1), 0.0)
    return pd.DataFrame({
        "component_size": comp_size, "component_distinct_applicants": comp_people,
        "max_entity_degree": max_deg, "neighbor_fraud_ratio": ratio,
    })

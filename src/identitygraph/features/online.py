"""Incremental feature computation for online scoring.

`build_features` recomputes every feature over the whole history, which is O(history) per scored application
(seconds locally, ~30 s on a small shared CPU). `OnlineFeaturizer` keeps per-entity state (timestamps, applicant
sets, label prefix sums) and a union-find over the history, so a new application's features cost O(log n) per
entity. It reproduces `build_features` exactly for the supported case (see tests/unit/test_online_features.py):
a new application that is not older than anything already in the history, with `label_scope: all_matured`.
Anything else raises `OnlineFallback` and the caller uses the full recompute.
"""
from __future__ import annotations

from bisect import bisect_left, bisect_right

import numpy as np
import pandas as pd

from ..config import load_config
from .graph_features import _DSU, epoch_seconds
from .pipeline import ENTITY_COLS, add_local_features

WINDOW_NAMES = {1: "1h", 24: "24h", 168: "7d"}
WINDOW_COLS = ("device_id", "ip_address")


class OnlineFallback(Exception):
    """The incremental path cannot reproduce the full recompute for this input; use build_features."""


class OnlineFeaturizer:
    def __init__(self, history: pd.DataFrame, cfg: dict | None = None):
        cfg = cfg or load_config("features")
        self.hours = list(cfg["velocity_windows_hours"])
        self.lag = int(cfg["label_maturity_days"]) * 86400
        self.supported = cfg.get("label_scope", "all_matured") == "all_matured"
        self.max_ts = -(1 << 62)
        self._ts = {c: {} for c in ENTITY_COLS}      # value -> ascending epoch seconds
        self._applicants = {c: {} for c in ENTITY_COLS}  # value -> set of applicant ids
        self._cum_known = {c: {} for c in ENTITY_COLS}   # value -> prefix counts of rows with a known label
        self._cum_fraud = {c: {} for c in ENTITY_COLS}   # value -> prefix counts of known fraud labels
        self._dsu = _DSU()
        h = history.sort_values("application_timestamp", kind="stable")
        ts = epoch_seconds(h["application_timestamp"])
        labels = (pd.to_numeric(h["fraud_label"], errors="coerce").to_numpy(dtype=float)
                  if "fraud_label" in h.columns else np.full(len(h), np.nan))
        cols = {c: h[c].to_numpy() for c in ENTITY_COLS}
        applicants = h["applicant_id"].to_numpy()
        for i in range(len(h)):
            self._add({c: cols[c][i] for c in ENTITY_COLS}, applicants[i], int(ts[i]), labels[i])

    # -- state ---------------------------------------------------------------------------------------
    def _add(self, values: dict, applicant, t: int, label: float) -> None:
        known = not np.isnan(label)
        for c in ENTITY_COLS:
            v = values[c]
            ts = self._ts[c].setdefault(v, [])
            ck = self._cum_known[c].setdefault(v, [0])
            cf = self._cum_fraud[c].setdefault(v, [0])
            ts.append(t)
            ck.append(ck[-1] + (1 if known else 0))
            cf.append(cf[-1] + (1 if known and label == 1 else 0))
            self._applicants[c].setdefault(v, set()).add(applicant)
        dsu = self._dsu
        node = ("app", len(dsu.parent), t)  # unique node id; only identity matters
        dsu.parent[node] = node
        dsu.apps[node] = 1
        dsu.people[node] = {applicant}
        for c in ENTITY_COLS:
            key = (c, values[c])
            dsu.parent.setdefault(key, key)
            dsu.apps.setdefault(key, 0)
            dsu.people.setdefault(key, set())
            dsu.union(node, key)
        self.max_ts = max(self.max_ts, t)

    # -- features ------------------------------------------------------------------------------------
    def _row_features(self, values: dict, applicant, t: int) -> dict:
        out: dict = {}
        total_known = fraud_known = 0
        max_deg = 0
        for c in ENTITY_COLS:
            v = values[c]
            ts = self._ts[c].get(v, [])
            out[f"{c}_prior_apps"] = len(ts)
            out[f"{c}_prior_distinct_applicants"] = len(self._applicants[c].get(v, ()))
            max_deg = max(max_deg, len(ts))
            if c in WINDOW_COLS:
                for h in self.hours:
                    out[f"{c}_apps_{WINDOW_NAMES[h]}"] = len(ts) - bisect_left(ts, t - h * 3600)
            if ts:
                upto = bisect_right(ts, t - self.lag)
                total_known += self._cum_known[c][v][upto]
                fraud_known += self._cum_fraud[c][v][upto]
        # connected component the new application would join (computed without mutating the union-find)
        dsu = self._dsu
        roots = {dsu.find((c, values[c])) for c in ENTITY_COLS if (c, values[c]) in dsu.parent}
        people = {applicant}
        size = 1
        for r in roots:
            size += dsu.apps.get(r, 0)
            people |= dsu.people.get(r, set())
        out["component_size"] = size
        out["component_distinct_applicants"] = len(people)
        out["max_entity_degree"] = max_deg
        out["neighbor_fraud_ratio"] = fraud_known / total_known if total_known > 0 else 0.0
        return out

    def features(self, new: pd.DataFrame, commit: bool = True) -> pd.DataFrame:
        """Featurise `new` (raw application columns, no labels) against the current state.

        commit=True adds the rows to the state so later calls see them (caller must discard the featurizer if
        anything fails afterwards). Raises OnlineFallback before touching any state if unsupported.
        """
        if not self.supported:
            raise OnlineFallback("label_scope != all_matured")
        new = new.reset_index(drop=True).copy()
        ts = epoch_seconds(new["application_timestamp"])
        if len(ts) and (ts.min() < self.max_ts or (np.diff(ts) < 0).any()):
            raise OnlineFallback("application older than existing history")
        add_local_features(new)
        cols = {c: new[c].to_numpy() for c in ENTITY_COLS}
        applicants = new["applicant_id"].to_numpy()
        rows = []
        for i in range(len(new)):
            values = {c: cols[c][i] for c in ENTITY_COLS}
            t = int(ts[i])
            rows.append(self._row_features(values, applicants[i], t))
            if commit:
                self._add(values, applicants[i], t, float("nan"))
        feats = pd.DataFrame(rows, index=new.index)
        for c in feats.columns:
            new[c] = feats[c]
        return new

"""Point-in-time feature engineering. Every feature for an application uses ONLY rows with an earlier
(or equal-earlier-in-order) timestamp. Labels are used only through `neighbor_fraud_ratio`, which
applies a maturity lag and a hard train-period cutoff (see graph_features.py)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import load_config
from .graph_features import epoch_seconds, graph_features

ENTITY_COLS = ["device_id", "ip_address", "email", "phone", "address"]
BASE_FEATURES = [
    "age", "income_to_credit_ratio", "log_income", "log_requested_credit", "hour", "day_of_week",
    "is_night", "email_name_mismatch", "young_high_credit",
    *[f"{c}_prior_apps" for c in ENTITY_COLS],
    *[f"{c}_prior_distinct_applicants" for c in ENTITY_COLS],
    "device_id_apps_1h", "device_id_apps_24h", "device_id_apps_7d",
    "ip_address_apps_1h", "ip_address_apps_24h", "ip_address_apps_7d",
]
GRAPH_FEATURES = [
    "component_size", "component_distinct_applicants", "max_entity_degree", "neighbor_fraud_ratio",
]
CATEGORICAL = ["employment_status", "application_channel"]


def _prior_counts(df: pd.DataFrame, col: str) -> tuple[np.ndarray, np.ndarray]:
    """Prior application count and prior distinct applicants for the same entity value."""
    prior_apps = df.groupby(col).cumcount().to_numpy()
    first_pair = ~df.duplicated(subset=[col, "applicant_id"])
    distinct_incl = first_pair.groupby(df[col]).cumsum().to_numpy()
    prior_distinct = distinct_incl - first_pair.to_numpy().astype(int)
    return prior_apps, prior_distinct


def _window_counts(df: pd.DataFrame, col: str, hours: list[int]) -> dict[str, np.ndarray]:
    ts = epoch_seconds(df["application_timestamp"])
    out = {h: np.zeros(len(df), dtype=int) for h in hours}
    for _, idx in df.groupby(col).indices.items():
        t = ts[idx]  # already sorted ascending because df is time-sorted
        pos = np.arange(len(idx))
        for h in hours:
            start = np.searchsorted(t, t - h * 3600, side="left")
            out[h][idx] = pos - start
    return out


def _name_email_mismatch(df: pd.DataFrame) -> np.ndarray:
    first = df["full_name"].str.split().str[0].str.lower()
    last = df["full_name"].str.split().str[-1].str.lower()
    local = df["email"].str.split("@").str[0].str.lower()
    ok = [(fn in e) and (ln in e) for fn, ln, e in zip(first, last, local, strict=True)]
    return (~np.array(ok)).astype(int)


def build_features(df: pd.DataFrame, train_end: pd.Timestamp | None = None,
                   cfg: dict | None = None) -> pd.DataFrame:
    """Return df (time-sorted) with engineered feature columns appended.

    train_end: labels from applications after this instant are never used by graph features.
    """
    cfg = cfg or load_config("features")
    df = df.sort_values("application_timestamp", kind="stable").reset_index(drop=True).copy()
    ts = df["application_timestamp"]
    dob = pd.to_datetime(df["date_of_birth"])
    df["age"] = (ts - dob).dt.days / 365.25
    df["income_to_credit_ratio"] = df["annual_income"] / df["requested_credit"].clip(lower=1)
    df["log_income"] = np.log1p(df["annual_income"])
    df["log_requested_credit"] = np.log1p(df["requested_credit"])
    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek
    df["is_night"] = ((df["hour"] < 6) | (df["hour"] >= 23)).astype(int)
    df["email_name_mismatch"] = _name_email_mismatch(df)
    df["young_high_credit"] = ((df["age"] < 23) & (df["requested_credit"] > df["annual_income"] * 0.5)).astype(int)

    for col in ENTITY_COLS:
        a, d = _prior_counts(df, col)
        df[f"{col}_prior_apps"] = a
        df[f"{col}_prior_distinct_applicants"] = d
    hours = cfg["velocity_windows_hours"]
    names = {1: "1h", 24: "24h", 168: "7d"}
    for col in ("device_id", "ip_address"):
        w = _window_counts(df, col, hours)
        for h in hours:
            df[f"{col}_apps_{names[h]}"] = w[h]

    # label_scope "all_matured": any earlier label older than the maturity lag is known in production
    # (delayed feedback). "train": legacy strict mode, only train-period labels (causes train/serve skew).
    cutoff = train_end if cfg.get("label_scope", "all_matured") == "train" else None
    gf = graph_features(df, ENTITY_COLS, train_end=cutoff,
                        maturity_days=cfg["label_maturity_days"])
    for c in GRAPH_FEATURES:
        df[c] = gf[c]
    return df

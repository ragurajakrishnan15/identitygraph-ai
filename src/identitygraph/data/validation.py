from __future__ import annotations

import pandas as pd

from .schemas import APPLICATION_COLUMNS, CHANNELS, EMPLOYMENT


def validate(df: pd.DataFrame, require_labels: bool = True) -> dict:
    errors: list[str] = []
    missing = [c for c in APPLICATION_COLUMNS if c not in df.columns]
    if missing:
        return {"ok": False, "errors": [f"missing columns: {missing}"], "missingness": {}}
    if require_labels and "fraud_label" not in df.columns:
        errors.append("missing fraud_label")
    if df["application_id"].duplicated().any():
        errors.append("duplicate application_id")
    if not set(df["employment_status"]).issubset(EMPLOYMENT):
        errors.append("invalid employment_status")
    if not set(df["application_channel"]).issubset(CHANNELS):
        errors.append("invalid application_channel")
    if (df["annual_income"] <= 0).any():
        errors.append("non-positive annual_income")
    if (df["requested_credit"] <= 0).any():
        errors.append("non-positive requested_credit")
    if "fraud_label" in df.columns and not set(df["fraud_label"].unique()).issubset({0, 1}):
        errors.append("fraud_label not in {0,1}")
    miss = df[APPLICATION_COLUMNS].isna().mean()
    if (miss > 0.05).any():
        errors.append(f"missingness > 5%: {miss[miss > 0.05].to_dict()}")
    return {
        "ok": not errors, "errors": errors, "n_rows": len(df),
        "missingness": {k: float(v) for k, v in miss.items()},
        "fraud_rate": float(df["fraud_label"].mean()) if "fraud_label" in df.columns else None,
    }

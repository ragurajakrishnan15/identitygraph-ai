from __future__ import annotations

import pandas as pd

from ..data.schemas import APPLICATION_COLUMNS
from ..data.validation import validate


def quality_report(df: pd.DataFrame) -> dict:
    v = validate(df, require_labels=False)
    miss = {k: float(x) for k, x in df[[c for c in APPLICATION_COLUMNS if c in df.columns]].isna().mean().items()}
    return {"schema_ok": v["ok"], "errors": v["errors"], "n_rows": len(df), "missingness": miss,
            "status": "pass" if v["ok"] else "fail"}

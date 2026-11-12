from __future__ import annotations

from pathlib import Path

import pandas as pd

from ..config import SYNTH_DIR


def load_applications(path: Path | None = None) -> pd.DataFrame:
    path = path or SYNTH_DIR / "applications.csv"
    return pd.read_csv(path, parse_dates=["application_timestamp"])

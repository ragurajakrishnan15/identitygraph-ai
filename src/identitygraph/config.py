from __future__ import annotations

import os
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "configs"
ARTIFACT_DIR = Path(os.getenv("IDENTITYGRAPH_ARTIFACT_DIR", ROOT / "artifacts"))
SYNTH_DIR = ROOT / "data" / "synthetic"
PROCESSED_DIR = Path(os.getenv("IDENTITYGRAPH_PROCESSED_DIR", ROOT / "data" / "processed"))
REPORT_DIR = ROOT / "reports"


def load_config(name: str) -> dict:
    with open(CONFIG_DIR / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)

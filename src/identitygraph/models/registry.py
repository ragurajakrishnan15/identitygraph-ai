from __future__ import annotations

import json
from pathlib import Path

import joblib

from ..config import ARTIFACT_DIR


def save_bundle(bundle: dict, path: Path | None = None) -> Path:
    path = path or ARTIFACT_DIR / "model.joblib"
    path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, path)
    return path


def load_bundle(path: Path | None = None) -> dict:
    path = path or ARTIFACT_DIR / "model.joblib"
    if not path.exists():
        raise FileNotFoundError(f"Model artifact not found at {path}. Run scripts/train.py first.")
    return joblib.load(path)


def save_json(obj: dict, name: str, directory: Path | None = None) -> Path:
    p = (directory or ARTIFACT_DIR) / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))
    return p


def load_json(name: str, directory: Path | None = None) -> dict:
    p = (directory or ARTIFACT_DIR) / name
    if not p.exists():
        raise FileNotFoundError(f"{p} not found. Run scripts/train.py / evaluate.py first.")
    return json.loads(p.read_text())

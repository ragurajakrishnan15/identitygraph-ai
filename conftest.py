"""Shared fixtures. Heavy fixtures use a SMALL synthetic set and temp dirs; no network or credentials."""
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

# Redirect artifacts/db to a temp dir BEFORE importing project modules.
_TMP = Path(tempfile.mkdtemp(prefix="idgraph_test_"))
os.environ["IDENTITYGRAPH_ARTIFACT_DIR"] = str(_TMP / "artifacts")
os.environ["IDENTITYGRAPH_PROCESSED_DIR"] = str(_TMP / "processed")
os.environ["WARM_ON_START"] = "0"
os.environ["DATABASE_URL"] = f"sqlite:///{(_TMP / 'test.db').as_posix()}"

import pytest  # noqa: E402

from identitygraph.data.generator import generate  # noqa: E402


@pytest.fixture(scope="session")
def small_df():
    return generate(n=2500, seed=7)


@pytest.fixture(scope="session")
def trained(small_df):
    from identitygraph.models.train import train_all

    return train_all(small_df)


@pytest.fixture(scope="session")
def seeded_app(trained):
    import pandas as pd

    from backend.app.db.seed import seed
    from backend.app.db.session import reset_engine
    from identitygraph.config import PROCESSED_DIR
    from identitygraph.models.registry import load_bundle, save_json
    from identitygraph.monitoring.snapshot import build_snapshot

    save_json(build_snapshot(load_bundle(), pd.read_parquet(PROCESSED_DIR / "features.parquet")), "monitoring.json")
    reset_engine(os.environ["DATABASE_URL"])
    seed()
    from backend.app.main import app

    return app

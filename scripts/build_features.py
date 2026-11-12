"""Build the leakage-safe feature table (also done inside train.py). Writes data/processed/features.parquet."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.config import PROCESSED_DIR, load_config  # noqa: E402
from identitygraph.data.ingestion import load_applications  # noqa: E402
from identitygraph.evaluation.splits import chronological_split  # noqa: E402
from identitygraph.features.pipeline import build_features  # noqa: E402

if __name__ == "__main__":
    df = load_applications()
    m = load_config("model")["split"]
    tr, va, te, train_end = chronological_split(df, m["train_frac"], m["val_frac"])
    feats = build_features(df, train_end=train_end)
    feats["split"] = ["train"] * len(tr) + ["val"] * len(va) + ["test"] * len(te)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    feats.to_parquet(PROCESSED_DIR / "features.parquet", index=False)
    print(f"wrote {len(feats)} rows x {feats.shape[1]} cols; train_end={train_end}")

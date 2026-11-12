"""Score the processed feature table with the saved model and write data/processed/scores.csv."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.config import PROCESSED_DIR  # noqa: E402
from identitygraph.decisioning.policy import display_score, tier_for  # noqa: E402
from identitygraph.models.predict import score_frame  # noqa: E402
from identitygraph.models.registry import load_bundle  # noqa: E402

if __name__ == "__main__":
    b = load_bundle()
    f = pd.read_parquet(PROCESSED_DIR / "features.parquet")
    f["score"] = score_frame(b, f)
    f["display_score"] = f["score"].map(display_score)
    f["tier"] = f["score"].map(lambda s: tier_for(s, b["thresholds"]))
    out = f[["application_id", "split", "score", "display_score", "tier"]]
    out.to_csv(PROCESSED_DIR / "scores.csv", index=False)
    print(out.tier.value_counts().to_string())

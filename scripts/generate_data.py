import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.config import SYNTH_DIR, load_config  # noqa: E402
from identitygraph.data.generator import generate  # noqa: E402
from identitygraph.data.schemas import DATA_DICTIONARY  # noqa: E402

if __name__ == "__main__":
    cfg = load_config("data")
    df = generate(cfg=cfg)
    SYNTH_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(SYNTH_DIR / "applications.csv", index=False)
    df.to_parquet(SYNTH_DIR / "applications.parquet", index=False)
    (SYNTH_DIR / "data_dictionary.json").write_text(json.dumps(DATA_DICTIONARY, indent=2))
    print(f"wrote {len(df)} rows, fraud rate {df.fraud_label.mean():.3%}")
    print(df.fraud_scenario.value_counts())

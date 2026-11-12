import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from identitygraph.data.ingestion import load_applications  # noqa: E402
from identitygraph.data.validation import validate  # noqa: E402

if __name__ == "__main__":
    res = validate(load_applications())
    print(json.dumps({k: v for k, v in res.items() if k != "missingness"}, indent=2))
    sys.exit(0 if res["ok"] else 1)

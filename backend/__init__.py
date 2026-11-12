import sys
from pathlib import Path

# Allow `uvicorn backend.app.main:app` from the repo root without installing the package.
_SRC = str(Path(__file__).resolve().parents[1] / "src")
if _SRC not in sys.path:
    sys.path.insert(0, _SRC)

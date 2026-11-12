#!/bin/sh
set -e
if [ ! -f artifacts/model.joblib ]; then
  echo "No model artifact: generating synthetic data and training (first start only)..."
  python scripts/generate_data.py
  python scripts/validate_data.py
  python scripts/train.py
  python scripts/evaluate.py
fi
python scripts/seed_db.py
exec uvicorn backend.app.main:app --host 0.0.0.0 --port 8000

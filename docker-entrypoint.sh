#!/bin/sh
set -e
if [ ! -f artifacts/model.joblib ]; then
  echo "No model artifact: generating synthetic data and training (first start only)..."
  python scripts/generate_data.py
  python scripts/validate_data.py
  python scripts/train.py
  python scripts/evaluate.py
fi
alembic upgrade head   # versioned schema migrations
python scripts/seed_db.py --if-empty
exec uvicorn backend.app.main:app --host 0.0.0.0 --port "${PORT:-8000}"

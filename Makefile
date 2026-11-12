PY ?= python
setup:; $(PY) -m pip install -r requirements-dev.txt
generate-data:; $(PY) scripts/generate_data.py
validate-data:; $(PY) scripts/validate_data.py
features:; $(PY) scripts/build_features.py
train:; $(PY) scripts/train.py
evaluate:; $(PY) scripts/evaluate.py
seed-db:; $(PY) scripts/seed_db.py
test:; $(PY) -m pytest -q
lint:; $(PY) -m ruff check .
api:; uvicorn backend.app.main:app --reload --port 8000
frontend:; cd frontend && npm install && npm run dev
docker-up:; docker compose up --build

# PROJECT_STATUS

Last updated: 2026-11-13. Everything below marked **verified** was actually run in this session.

## Done
- Synthetic generator (20k rows, seeded, 7 scenarios), schema/quality validation, data card, data dictionary. **verified**: `generate_data.py`, `validate_data.py`
- Point-in-time features (reuse, velocity 1h/24h/7d, age, ratio, identity flags, time) + union-find graph features + matured/train-only neighbor-fraud ratio. **verified** by unit tests
- Chronological split; 4 models; validation-only thresholds; artifacts; model card; evaluation summary. **verified**: `train.py`, `evaluate.py`
- NetworkX identity graph + React-Flow serialization; SHAP explanations (fallback implemented); decision policy; monitoring (PSI, drift, quality, score/tier distribution)
- FastAPI (all spec endpoints + `/overview`, notes, entity search), SQLAlchemy DB (SQLite; Postgres via compose), seed script. **verified**: API tests + live curl (health, CORS preflight, list)
- Next.js frontend: Overview, Score, Applications (+drawer), Application detail, Network, Models, Monitoring, Features, Reports (CSV export). **verified**: `npm run lint`, `tsc --noEmit`, `next build` all pass
- Tests: 21 pytest tests pass (unit, integration, API). `ruff check .` clean. **verified**
- Dockerfiles, docker-compose (backend, frontend, Postgres, healthchecks, volume), CI workflow, README. **verified**: `docker compose up --build` trained inside the container, seeded Postgres, API healthy, frontend served; same metrics as the local run
- Browser UI smoke test (`tests/e2e/ui_smoke.py`, Playwright + Edge): 21 checks (form validation, scoring, filters, search, pagination, drawer, notes, graph links/search/select, model switch, CSV export) pass against the Docker stack
- 3 notebooks in `notebooks/` (generated + executed by `scripts/make_notebooks.py`; outputs come from the real artifacts)
- Found and fixed via that test: the network graph's ring layout overlapped nodes and blocked clicks; edge labels removed to cut clutter

## Pending / known gaps (honest list)
- **CI workflow not executed** on GitHub (nothing pushed; needs a remote).
- UI smoke test had one unexplained one-off failure (score page showed no mock banner on re-runs); not reproduced in 3 later runs.
- Alembic migrations, XGBoost/LightGBM/MLflow, IEEE-CIS track and Framer Motion polish are not implemented.
- Graph-enhanced model does not beat the baseline on PR-AUC (reported as measured). Likely cause: `neighbor_fraud_ratio` is ~always 0 in val/test but informative in train (train/serve skew); see reports/model_card.md. Not yet fixed.
- New-application scoring takes ~4-5 s (recomputes features over history); not low-latency.
- Monitoring is batch (train vs test), not real-time; no persistent online-score monitoring.
- Synthetic metrics are optimistic; scores are uncalibrated.
- Bug found and fixed during testing: pandas 3 datetime unit assumption broke velocity windows/maturity lag on non-ns datetimes (now unit-safe, regression-tested).

## Run commands
```
pip install -r requirements-dev.txt
python scripts/generate_data.py && python scripts/validate_data.py
python scripts/train.py && python scripts/evaluate.py && python scripts/seed_db.py
uvicorn backend.app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
pytest -q && ruff check .
```

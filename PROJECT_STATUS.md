# PROJECT_STATUS

Last updated: 2026-11-13. Items marked **verified** were actually run in this session.

## Done
- Synthetic generator (20k rows, seeded, 7 scenarios), validation, data card/dictionary. **verified**
- Point-in-time features + union-find graph features + neighbour-fraud ratio (label-maturity lag, `label_scope` all_matured|train). **verified** by unit tests, including a leakage test per mode
- Chronological split; **8 models** (LR, RF, GB/XGBoost/LightGBM each with and without graph features); validation-only thresholds with a 15% review-capacity cap; model card; evaluation summary. **verified**
- NetworkX identity graph, SHAP explanations, decision policy, PSI monitoring. FastAPI (all spec endpoints + overview, notes, entity search); SQLAlchemy + **Alembic migrations** (up/down tested on SQLite; run on container start against Postgres). **verified**
- **Apple-style Next.js UI**: landing page (hero, results, limits), frosted top nav, light/dark themes, Framer Motion reveals, 1/2-hop network toggle. `lint`, `tsc`, `next build` pass. **verified**
- Tests: 22 pytest tests pass; `ruff check .` clean; **24/24 browser checks** pass against the Docker stack (Postgres). **verified**
- Docker Compose (model built into the image, so start-up takes seconds), Render blueprint, Vercel config, `docs/DEPLOYMENT.md`, README with screenshots, 3 executed notebooks.
- Pushed to https://github.com/ragurajakrishnan15/identitygraph-ai; **GitHub CI green** (backend + frontend jobs)

## Pending / known gaps (honest list)
- **Not yet deployed.** Configs and steps are ready (`docs/DEPLOYMENT.md`); deploying needs the owner's Vercel and Render accounts.
- Graph lift (+0.015 PR-AUC) relies on a 7-day label-maturity lag chosen after seeing test results (one alternative tried); single seed, no confidence intervals.
- MLflow and the IEEE-CIS real-data track are not implemented (the separate FraudShield project covers IEEE-CIS).
- New-application scoring takes ~4-5 s (recomputes features over history). Monitoring is batch only. Synthetic metrics are optimistic; scores are uncalibrated.
- One earlier unexplained one-off UI smoke failure (not reproduced in many later runs).

## Run commands
```
pip install -r requirements-dev.txt
python scripts/generate_data.py && python scripts/validate_data.py
python scripts/train.py && python scripts/evaluate.py && python scripts/seed_db.py
uvicorn backend.app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
pytest -q && ruff check .
docker compose up --build
```

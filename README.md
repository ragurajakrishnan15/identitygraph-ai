# IdentityGraph AI

A portfolio fraud-risk investigation platform: generate synthetic credit-application data, engineer
leakage-safe identity/device/velocity/graph features, train and evaluate models, serve scores via a
FastAPI API, explain predictions, monitor drift, and explore everything in a Next.js analyst dashboard.

> **All data is synthetic and all decisions are simulated.** This is not a real credit-decision system.
> Graph links are investigation signals, not proof of fraud. Scores are **uncalibrated** (not probabilities).

## Architecture

```
generator -> validation -> feature pipeline (point-in-time) -> chronological split -> models
                                  |                                        |
                         union-find graph features               thresholds (validation only)
                                  v                                        v
 SQLite/Postgres <- seed <- artifacts (model.joblib, metrics.json, monitoring.json)
        |
 FastAPI (route -> service -> repository) -> Next.js dashboard (API client + labelled mock fallback)
```

| Path | Purpose |
|---|---|
| `src/identitygraph/` | data, features, graph, models, evaluation, explainability, monitoring, decisioning |
| `backend/app/` | FastAPI app, services, SQLAlchemy repositories, API tests |
| `frontend/` | Next.js (App Router) + Tailwind + Recharts + React Flow |
| `configs/` | data, features, model, thresholds, app YAML |
| `scripts/` | generate / validate / build_features / build_graph / train / evaluate / batch_score / seed_db |
| `reports/` | data card, model card, evaluation summary |

## Quick start (Windows PowerShell or any shell)

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1          # PowerShell;  source .venv/bin/activate on Linux/macOS
pip install -r requirements-dev.txt
python scripts/generate_data.py     # 20k seeded synthetic applications
python scripts/validate_data.py
python scripts/train.py             # chronological split, 4 models, saves artifacts/
python scripts/evaluate.py          # monitoring snapshot + reports/evaluation_summary.md
python scripts/seed_db.py           # SQLite DB (identitygraph.db), scores + explanations + graph
uvicorn backend.app.main:app --reload --port 8000
cd frontend && npm install && cp .env.example .env.local && npm run dev   # http://localhost:3000
```

`make setup generate-data validate-data features train evaluate seed-db test lint api frontend docker-up` are provided as equivalents.
The API docs are at http://localhost:8000/docs. Without a running API the UI shows a clear
**"SIMULATED mock data"** banner (mock data lives only in `frontend/lib/mock-api.ts`).

## API (`/api/v1`)

`GET /health`, `GET /health/ready` · `GET /applications` (q, tier, channel, sort, order, page, page_size) ·
`GET /applications/{id}` · `GET /applications/{id}/explanation` · `POST /applications/{id}/notes` ·
`POST /score` · `POST /score/batch` (max 100) · `GET /entities?q=` · `GET /entities/{entity_id}/network` ·
`GET /models` · `GET /metrics/model` · `GET /metrics/monitoring` · `GET /features` · `GET /overview`.

Scoring requests reject label fields (`extra="forbid"`). Responses carry `is_simulated: true`.

## Leakage safeguards (tested in `tests/unit`)

- Chronological train / validation / test split; preprocessing is fit on train only.
- Every feature is computed from strictly earlier rows (point-in-time test: appending later rows never changes earlier features).
- `neighbor_fraud_ratio` uses only labels that are matured (>= 30 days old) **and** from the train period; changing future labels leaves features unchanged (tested).
- Decision thresholds are selected on the validation split only.

## Results

See [reports/evaluation_summary.md](reports/evaluation_summary.md) and [reports/model_card.md](reports/model_card.md).
Metrics are measured on synthetic data and are likely optimistic relative to real fraud. The graph-enhanced
model did **not** beat the plain gradient-boosting baseline on PR-AUC (0.827 vs 0.830) and that is reported as measured.

## Limitations

Synthetic data only; uncalibrated scores; scoring a new application recomputes features over the full
history (a few seconds, not low-latency); monitoring is batch (train vs held-out period), not real-time;
the optional IEEE-CIS track (transaction fraud, a different label meaning) is not included.

## Tests / CI

`pytest -q` (unit, integration on a 2,500-row fixture, API tests with a throwaway DB), `ruff check .`,
and in `frontend/`: `npm run lint`, `npm run typecheck`, `npm run build`. CI: `.github/workflows/ci.yml`.

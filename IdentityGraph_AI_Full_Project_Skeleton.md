# IdentityGraph AI — Full Project Skeleton

This is the **full-stack project skeleton**, not merely a UI design. Paste the included Master Prompt into Claude Code from your existing project folder. Claude Code should inspect and preserve the repository, then implement the modules below.

## Product scope
IdentityGraph AI is a portfolio fraud-risk investigation platform: ingest/generate synthetic credit-application data, validate it, engineer identity/device/behavioral/temporal/graph features, train and evaluate models, serve scores via API, explain predictions, monitor data/model behavior, and expose an analyst dashboard. The decision workflow is demonstrative only—not a real credit decision system.

**Data honesty:** Primary dataset is generated synthetic data. Optional IEEE-CIS Kaggle data represents transaction fraud and does not directly label synthetic identity fraud. Keep datasets/labels separate and document the distinction. Do not invent model metrics.

## Stack
- Python 3.11+, pandas, NumPy, scikit-learn, NetworkX; optional XGBoost/LightGBM, SHAP, MLflow
- FastAPI, Pydantic, Uvicorn, SQLAlchemy, PostgreSQL (SQLite local fallback), pytest/httpx
- Next.js App Router, TypeScript, Tailwind, shadcn/ui, Lucide, Recharts, React Flow, Framer Motion
- Docker/Compose, GitHub Actions, Ruff, ESLint, TypeScript checks

## Repository tree
```text
IdentityGraph-AI/
├── README.md                 # architecture, setup, results, limitations, API
├── PROJECT_STATUS.md         # progress, runnable commands, known gaps
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── Makefile
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
├── configs/{data,features,model,thresholds,app}.yaml
├── data/{README.md,raw/,processed/,synthetic/,samples/}   # generated data ignored
├── artifacts/                # model/metrics artifacts ignored
├── reports/{data_card.md,model_card.md,evaluation_summary.md}
├── notebooks/{01_data_exploration,02_feature_analysis,03_model_experiments}.ipynb
├── scripts/{generate_data,validate_data,build_features,build_graph,train,evaluate,batch_score,seed_db}.py
├── src/identitygraph/
│   ├── config.py
│   ├── data/{generator,ingestion,schemas,validation}.py
│   ├── features/{identity,device,temporal,behavioral,graph_features,pipeline}.py
│   ├── graph/{builder,analytics,serialization}.py
│   ├── models/{baseline,train,predict,registry,thresholds}.py
│   ├── evaluation/{metrics,splits,report}.py
│   ├── explainability/explanations.py
│   ├── monitoring/{data_quality,drift,prediction_stats}.py
│   └── decisioning/policy.py
├── backend/app/
│   ├── main.py
│   ├── core/{config,logging}.py
│   ├── dependencies.py
│   ├── api/routes/{health,applications,scoring,entities,models,monitoring}.py
│   ├── api/schemas/{application,scoring,graph,metrics}.py
│   ├── services/{application,scoring,graph,model,monitoring}_service.py
│   ├── db/{session,models,repositories}.py
│   └── tests/{test_health,test_scoring,test_applications,test_entities}.py
├── frontend/
│   ├── app/{layout,page,loading,error,not-found}.tsx
│   ├── app/(dashboard)/{overview,score,applications,network,models,monitoring,features,reports}/page.tsx
│   ├── app/(dashboard)/applications/[id]/page.tsx
│   ├── components/{shell,dashboard,applications,scoring,graph,models,monitoring,charts,ui}/
│   ├── lib/{api-client,mock-api,utils,validators}.ts
│   ├── hooks/
│   ├── types/{application,scoring,graph,metrics}.ts
│   ├── public/
│   └── package.json
├── tests/{unit,integration}/
└── .github/workflows/ci.yml
```

## Data contract
Application fields: `application_id`, `applicant_id`, `application_timestamp`, `full_name`, `date_of_birth`, `email`, `phone`, `address`, `device_id`, `ip_address`, `employment_status`, `annual_income`, `requested_credit`, `application_channel`. Training-only columns: `fraud_label` (0/1), `fraud_scenario`. Never accept labels in online scoring request.

Scoring response should include: application ID, score/probability (clearly call it probability only if calibrated), 0–100 display score, tier, simulated recommendation, model version, scored timestamp, top factors, linked entity summaries, and `is_simulated`.

## Data generation / ingestion
Generate configurable ≥20k reproducible records, seeded, with scenarios: legitimate applications, simulated synthetic identities, device-sharing rings, shared address/phone/email/IP, bursts of application velocity, identity inconsistencies, unusual income/credit ratio. Output CSV/Parquet, data dictionary and generator assumptions. Add schema and quality validation.

## Feature engineering
- Device/IP/email/phone/address reuse and distinct applicants
- Application velocity windows 1h/24h/7d
- DOB-derived age as of application time
- Income/requested-credit ratio
- Identity consistency flags
- Time-of-day/day-of-week
- Graph degree, component size, optionally clustering coefficient
- Historical fraud-neighbor ratio only from labels known before timestamp and only train-period data

**Leakage prevention:** chronological train/validation/test splits; no future counts, future outcomes, or validation/test labels in graph features; fit encoders/scalers on train only; document and test protections.

## Identity graph
NetworkX graph nodes: applicant, application, device, email, phone, IP, address. Edges reflect “associated with/used/submitted from.” Compute degree, connected component size, entity sharing and neighborhood summaries. Serialize nodes/edges for React Flow. In UI, connections are investigation signals—not proof of fraud.

## Model pipeline
Train at least Logistic Regression, Random Forest, sklearn Gradient Boosting (optional XGBoost/LightGBM), and graph-enhanced model with graph features. Save preprocessing, model, feature list, version, metrics and reports.

Evaluate chronological holdout using PR-AUC (primary), ROC-AUC, precision, recall, F1, confusion matrix, recall at 1% FPR; optional precision at review budget and calibration. Select thresholds on validation only. Report graph-enhanced result honestly even if it does not improve performance.

Explainability: SHAP if available/practical; fallback to coefficients or feature importance. Show per-case factors in understandable language; do not imply causal proof.

## Decision policy
Configurable thresholds in `configs/thresholds.yaml`. Demo recommendations: Low = low-risk recommendation; Medium = manual review; High = enhanced investigation. Do not auto-decline real credit.

## FastAPI endpoints (`/api/v1`)
- `GET /health`, `GET /health/ready`
- `GET /applications` (search/filter/pagination)
- `GET /applications/{application_id}`
- `POST /score`, `POST /score/batch`
- `GET /applications/{application_id}/explanation`
- `GET /entities/{entity_id}/network`
- `GET /models`, `GET /metrics/model`, `GET /metrics/monitoring`, `GET /features`

Use Pydantic contracts, route→service→repository layering, CORS config, logging, meaningful errors and pagination. Keep ML logic out of route handlers.

## Database
SQLAlchemy tables: applications, scores, entities, entity_edges, model_versions, monitoring_snapshots, optional investigation_notes. PostgreSQL via Compose; SQLite for local quick start. Seed utility and optional Alembic migrations.

## Frontend pages
- Overview: KPIs, risk trend, distribution, channels, graph preview, recent cases
- Score Application: validated form, staged loading, score/tier/factors/network preview
- Application Explorer: search/filter/sort/pagination/detail drawer
- Application Detail: profile, risk assessment, factors, graph links, activity timeline, notes
- Identity Network: interactive React Flow, entity legend/search/focus/details, ring highlighting
- Model Performance: PR/ROC, confusion matrix, model comparison, feature importance
- Monitoring: drift/PSI, missingness, score distribution, quality status
- Feature Analysis: groups, importance, distributions
- Reports & Insights: preview and CSV export

Premium dark fintech design: navy background, violet/indigo accents, teal safe, amber medium, rose high risk. All interactions work. Centralize mock data; clearly label simulated fallbacks. Configure frontend API base URL via `.env.example`.

## Monitoring
Implement schema/missingness checks, PSI with configurable bins, feature drift, score/tier distributions, and label-based performance only when labels have matured. Display timestamp and batch/real-time limitations honestly.

## Tests
Unit tests: generator reproducibility/schema, feature calculations and windows, leakage-safe split, graph structure/components, metric calculations, policy thresholds, model artifact load and scoring.
API tests: health, validation, single/batch scoring, filters/pagination, explanation, network endpoints.
Integration test: generate small fixture → validate → feature pipeline → train → evaluate → save/load → score.
Frontend: lint, typecheck, build. CI should use small fixtures and not require external credentials or massive downloads.

## Dev commands
Document Make targets or equivalents:
```bash
make setup generate-data validate-data features train evaluate test lint api frontend docker-up
```
Simple local route:
```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
python scripts/generate_data.py
python scripts/validate_data.py
python scripts/build_features.py
python scripts/train.py
python scripts/evaluate.py
uvicorn backend.app.main:app --reload --port 8000
cd frontend && npm install && npm run dev
```

## Docker and CI
Compose services: backend, frontend, PostgreSQL with health checks and persistent volume. No committed secrets. CI: install Python, Ruff, pytest; install Node, lint/typecheck/build. Include `.env.example`, README, data card, model card, evaluation report. CI uses small fixture.

---

# MASTER PROMPT — Paste into Claude Code

You are a senior ML engineer, fraud risk data scientist, backend architect, and full-stack developer. Implement the **complete IdentityGraph AI full-stack project skeleton and runnable MVP** in this repository. This is not UI-only.

1. Inspect the repository/environment first. Preserve useful code, conventions and existing implementation; do not overwrite blindly.
2. Implement all: data generation/ingestion, validation, feature engineering, graph analytics, ML training/evaluation, explainability, decision policy, FastAPI, database, frontend, monitoring, tests, docs, Docker and CI.
3. Do not merely output a plan; create files and implement.
4. Use phases, run checks and fix observed failures.
5. Make reasonable decisions without unnecessary questions. Use fallback for optional dependencies.
6. Synthetic data must be identified as synthetic. Do not misrepresent IEEE-CIS transaction fraud labels as synthetic identity labels.
7. Do not fabricate metrics or claim checks/deployments that were not run.
8. Prevent time/target leakage and use chronological splits.
9. Mock data must be centralized and clearly marked; connect frontend to API when practical.
10. Do not push, deploy, or perform destructive external actions without asking.
11. Keep `PROJECT_STATUS.md` updated with done/pending, known limitations, exact run commands and tests.

### Phase order
A. Inspect repo; contracts, configs, dependencies and skeleton docs.
B. Synthetic data generator, schema validation and data card.
C. Feature engineering, identity graph and leakage safeguards.
D. Baseline/graph-enhanced model, time splits, metrics, thresholds, artifacts, model card.
E. FastAPI, service/repository structure, database, endpoints and API tests.
F. Frontend shell, all pages, functional interactions and API client/mock fallback.
G. Explainability, monitoring, drift and metrics UI.
H. Unit/integration tests, lint/typecheck/build, Docker/CI, README and runbook.

After each phase, summarize files touched and checks actually run. Continue through phases until a runnable end-to-end MVP exists. Begin by inspecting the repository and proceed with Phase A now.

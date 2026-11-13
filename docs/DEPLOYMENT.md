# Deployment

Recommended: **Vercel** for the Next.js frontend and **Render** (free Docker web service) for the FastAPI backend.
Vercel hosts the frontend only; the Python/ML backend needs a container host.

## 1. Backend on Render
1. Render dashboard > New > **Blueprint** > pick this repo (it reads `render.yaml`) > deploy.
2. First build takes several minutes: the image generates the synthetic data and trains the models, so the container starts in seconds.
3. Note the URL, e.g. `https://identitygraph-api.onrender.com`. Check `https://<url>/api/v1/health`.
4. Free instances sleep after ~15 min idle; the first request then takes ~30-60 s. The frontend shows a loading state, and falls back to a clearly labelled *simulated* banner if the API is unreachable.

## 2. Frontend on Vercel
1. Vercel > Add New > Project > import this repo > **Root Directory: `frontend`**.
2. Environment variable: `NEXT_PUBLIC_API_BASE_URL` = `https://<render-url>/api/v1`.
3. Deploy. Then set Render's `CORS_ORIGINS` to your Vercel URL (preview URLs are already allowed by `CORS_ORIGIN_REGEX`).

CLI alternative: `cd frontend && npx vercel --prod` (set the env var with `vercel env add NEXT_PUBLIC_API_BASE_URL production`).

## Other options
Fly.io, Railway or Google Cloud Run also run the root `Dockerfile` unchanged (it honours `$PORT`). For a persistent database set `DATABASE_URL` to a Postgres URL; schema is managed by Alembic (`alembic upgrade head` runs on container start).

## Notes
- All data is synthetic; no secrets are needed. Never commit real credentials.
- `docker compose up --build` runs the full stack locally (Postgres + API + UI).

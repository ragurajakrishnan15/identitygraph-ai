from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import applications, entities, health, models, scoring
from .core.config import get_settings
from .core.logging import setup_logging
from .db.session import init_db

log = logging.getLogger("identitygraph")


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    init_db()
    log.info("IdentityGraph AI API started (synthetic data; simulated decisions)")
    yield


def create_app() -> FastAPI:
    s = get_settings()
    app = FastAPI(title="IdentityGraph AI", version="0.1.0", lifespan=lifespan,
                  description="Portfolio fraud-risk platform on SYNTHETIC data. Decisions are simulated.")
    app.add_middleware(CORSMiddleware, allow_origins=s.cors_origins, allow_methods=["*"], allow_headers=["*"])
    for r in (health, applications, scoring, entities, models):
        app.include_router(r.router, prefix=s.api_prefix)
    return app


app = create_app()

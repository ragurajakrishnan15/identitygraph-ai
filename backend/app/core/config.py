from __future__ import annotations

import os
from functools import lru_cache

from identitygraph.config import ROOT


class Settings:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT / 'identitygraph.db').as_posix()}")
        self.cors_origins = [o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")]
        self.api_prefix = "/api/v1"


@lru_cache
def get_settings() -> Settings:
    return Settings()

from __future__ import annotations

from ..db.repositories import MonitoringRepository


def latest_snapshot():
    return MonitoringRepository().latest()

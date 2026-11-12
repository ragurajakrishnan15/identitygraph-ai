from __future__ import annotations

from datetime import datetime, timezone

from ..db.repositories import ApplicationRepository, NoteRepository
from . import graph_service

repo = ApplicationRepository()
notes = NoteRepository()


def list_applications(**kw):
    return repo.list(**kw)


def get_application(application_id: str):
    a = repo.get(application_id)
    if a is None:
        return None
    a["linked_entities"] = graph_service.links_for_application(application_id)
    a["notes"] = notes.list(application_id)
    events = [{"event": "Application submitted", "at": a["application_timestamp"]}]
    if a["score"]:
        events.append({"event": f"Scored: {a['score']['tier']} risk (model {a['score']['model_version']})",
                       "at": a["score"]["scored_at"]})
    events += [{"event": "Analyst note added", "at": n["created_at"]} for n in reversed(a["notes"])]
    a["timeline"] = events
    return a


def add_note(application_id: str, text: str):
    notes.add(application_id, text, datetime.now(timezone.utc).isoformat())
    return notes.list(application_id)

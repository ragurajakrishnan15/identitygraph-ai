import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))
from backend.app.db.seed import seed  # noqa: E402


def _is_empty() -> bool:
    from sqlalchemy import func, select

    from backend.app.db.models import ApplicationRow
    from backend.app.db.session import get_session, init_db
    init_db()
    with get_session() as db:
        return db.execute(select(func.count()).select_from(ApplicationRow)).scalar_one() == 0


if __name__ == "__main__":
    # --if-empty: skip when already seeded. Seeding scores + explains every row and needs >512 MB, so the
    # image seeds its default SQLite DB at build time and start-up only seeds an empty (e.g. Postgres) DB.
    if "--if-empty" in sys.argv and not _is_empty():
        print("database already seeded; skipping")
    else:
        print(seed())

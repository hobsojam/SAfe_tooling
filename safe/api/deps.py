import os
from contextlib import asynccontextmanager
from pathlib import Path

from tinydb import TinyDB

from safe.store.repos import Repos

_DEFAULT_DB_PATH = Path.home() / ".safe_tooling" / "db.json"
_DEV_SESSION_FILE = ".dev_session"

_db: TinyDB | None = None


def _dev_session_file(db_path: Path) -> Path:
    return db_path.parent / _DEV_SESSION_FILE


def _is_hot_reload(db_path: Path) -> bool:
    """True when this startup is a hot-reload of the same uvicorn session.

    uvicorn --reload keeps the supervisor (parent) process alive across
    hot reloads while only restarting the worker. Comparing os.getppid()
    against the value written on the previous startup lets us distinguish
    a hot reload (same parent PID) from a fresh server start (new PID).
    """
    session_file = _dev_session_file(db_path)
    if session_file.exists():
        return session_file.read_text().strip() == str(os.getppid())
    return False


def _write_dev_session(db_path: Path) -> None:
    _dev_session_file(db_path).write_text(str(os.getppid()))


@asynccontextmanager
async def lifespan(app):
    global _db
    path = Path(os.environ.get("SAFE_DB_PATH", str(_DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    _db = TinyDB(path)
    if os.environ.get("SAFE_SEED_DEV") == "1":
        from safe.dev_seed import seed

        if not _is_hot_reload(path):
            # Fresh server start: wipe the dev DB so data never persists across
            # restarts. Safe here because SAFE_SEED_DEV=1 only applies to the
            # dev database, never to the real user database.
            for table_name in _db.tables():
                _db.table(table_name).truncate()
            _write_dev_session(path)

        seed(Repos(_db))
    yield
    if _db is not None:
        _db.close()
        _db = None


def get_repos_dep() -> Repos:
    # TinyDB defines __len__, so an empty database is falsy — use identity check.
    if _db is None:
        raise RuntimeError("Database not initialised — lifespan not running")
    return Repos(_db)


def clear_cache() -> None:
    if _db is not None:
        for table_name in _db.tables():
            _db.table(table_name).clear_cache()

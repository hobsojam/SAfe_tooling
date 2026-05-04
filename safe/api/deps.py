import os
from contextlib import asynccontextmanager
from pathlib import Path

from tinydb import TinyDB

from safe.store.repos import Repos

_DEFAULT_DB_PATH = Path.home() / ".safe_tooling" / "db.json"

_db: TinyDB | None = None


@asynccontextmanager
async def lifespan(app):
    global _db
    path = Path(os.environ.get("SAFE_DB_PATH", str(_DEFAULT_DB_PATH)))
    path.parent.mkdir(parents=True, exist_ok=True)
    _db = TinyDB(path)
    if os.environ.get("SAFE_SEED_DEV") == "1":
        from safe.dev_seed import seed

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

from pathlib import Path

from tinydb import TinyDB

_DB_PATH = Path.home() / ".safe_tooling" / "db.json"
_instance: TinyDB | None = None


def get_db(path: Path | None = None) -> TinyDB:
    global _instance
    if path is not None:
        return TinyDB(path)
    if _instance is None:
        _DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _instance = TinyDB(_DB_PATH)
    return _instance


def close_db() -> None:
    global _instance
    if _instance is not None:
        _instance.close()
        _instance = None

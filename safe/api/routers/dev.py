from fastapi import APIRouter

from safe.api.deps import clear_cache

router = APIRouter(prefix="/dev", tags=["dev"])


@router.post("/reset-db", status_code=204)
def reset_db() -> None:
    """Clear TinyDB's in-memory query cache so e2e tests see fresh fixture data."""
    clear_cache()

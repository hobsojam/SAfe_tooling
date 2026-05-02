from fastapi import APIRouter, Depends, HTTPException

from safe.api.deps import get_repos_dep
from safe.api.schemas import ARTCreate, ARTUpdate
from safe.models.art import ART
from safe.store.repos import Repos

router = APIRouter(prefix="/art", tags=["ARTs"])


def _get_or_404(repos: Repos, art_id: str) -> ART:
    art = repos.arts.get(art_id)
    if art is None:
        raise HTTPException(status_code=404, detail=f"ART '{art_id}' not found")
    return art


@router.get("", response_model=list[ART])
def list_arts(repos: Repos = Depends(get_repos_dep)):
    return repos.arts.get_all()


@router.post("", response_model=ART, status_code=201)
def create_art(body: ARTCreate, repos: Repos = Depends(get_repos_dep)):
    art = ART(name=body.name)
    return repos.arts.save(art)


@router.get("/{art_id}", response_model=ART)
def get_art(art_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, art_id)


@router.patch("/{art_id}", response_model=ART)
def update_art(art_id: str, body: ARTUpdate, repos: Repos = Depends(get_repos_dep)):
    art = _get_or_404(repos, art_id)
    updated = art.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.arts.save(updated)


@router.delete("/{art_id}", status_code=204)
def delete_art(art_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, art_id)
    repos.arts.delete(art_id)

from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import DependencyCreate, DependencyROAM, DependencyUpdate
from safe.models.dependency import Dependency
from safe.store.repos import Repos

router = APIRouter(prefix="/dependencies", tags=["Dependencies"])


def _get_or_404(repos: Repos, dependency_id: str) -> Dependency:
    dep = repos.dependencies.get(dependency_id)
    if dep is None:
        raise HTTPException(status_code=404, detail=f"Dependency '{dependency_id}' not found")
    return dep


@router.get("", response_model=list[Dependency])
def list_dependencies(
    pi_id: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    if pi_id is not None:
        return repos.dependencies.find(pi_id=pi_id)
    return repos.dependencies.get_all()


@router.post("", response_model=Dependency, status_code=201)
def create_dependency(body: DependencyCreate, repos: Repos = Depends(get_repos_dep)):
    dep = Dependency(**body.model_dump())
    return repos.dependencies.save(dep)


@router.get("/{dependency_id}", response_model=Dependency)
def get_dependency(dependency_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, dependency_id)


@router.patch("/{dependency_id}", response_model=Dependency)
def update_dependency(dependency_id: str, body: DependencyUpdate, repos: Repos = Depends(get_repos_dep)):
    dep = _get_or_404(repos, dependency_id)
    updated = dep.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.dependencies.save(updated)


@router.post("/{dependency_id}/roam", response_model=Dependency)
def roam_dependency(dependency_id: str, body: DependencyROAM, repos: Repos = Depends(get_repos_dep)):
    dep = _get_or_404(repos, dependency_id)
    updated = dep.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.dependencies.save(updated)


@router.delete("/{dependency_id}", status_code=204)
def delete_dependency(dependency_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, dependency_id)
    repos.dependencies.delete(dependency_id)

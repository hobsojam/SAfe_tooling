from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import DependencyCreate, DependencyStatusUpdate, DependencyUpdate
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
    from_feature_id: str | None = Query(default=None),
    to_feature_id: str | None = Query(default=None),
    status: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    deps = repos.dependencies.find(pi_id=pi_id) if pi_id else repos.dependencies.get_all()
    if from_feature_id:
        deps = [d for d in deps if d.from_feature_id == from_feature_id]
    if to_feature_id:
        deps = [d for d in deps if d.to_feature_id == to_feature_id]
    if status:
        deps = [d for d in deps if d.status == status]
    return deps


@router.post("", response_model=Dependency, status_code=201)
def create_dependency(body: DependencyCreate, repos: Repos = Depends(get_repos_dep)):
    dep = Dependency(**body.model_dump())
    return repos.dependencies.save(dep)


@router.get("/{dependency_id}", response_model=Dependency)
def get_dependency(dependency_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, dependency_id)


@router.patch("/{dependency_id}", response_model=Dependency)
def update_dependency(
    dependency_id: str, body: DependencyUpdate, repos: Repos = Depends(get_repos_dep)
):
    dep = _get_or_404(repos, dependency_id)
    updated = dep.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.dependencies.save(updated)


@router.post("/{dependency_id}/update-status", response_model=Dependency)
def update_dependency_status(
    dependency_id: str, body: DependencyStatusUpdate, repos: Repos = Depends(get_repos_dep)
):
    dep = _get_or_404(repos, dependency_id)
    updated = dep.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.dependencies.save(updated)


@router.delete("/{dependency_id}", status_code=204)
def delete_dependency(dependency_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, dependency_id)
    repos.dependencies.delete(dependency_id)

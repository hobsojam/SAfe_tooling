from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import PIObjectiveCreate, PIObjectiveUpdate
from safe.models.objectives import PIObjective
from safe.store.repos import Repos

router = APIRouter(prefix="/objectives", tags=["Objectives"])


def _get_or_404(repos: Repos, objective_id: str) -> PIObjective:
    obj = repos.objectives.get(objective_id)
    if obj is None:
        raise HTTPException(status_code=404, detail=f"Objective '{objective_id}' not found")
    return obj


@router.get("", response_model=list[PIObjective])
def list_objectives(
    pi_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    filters = {k: v for k, v in {"pi_id": pi_id, "team_id": team_id}.items() if v is not None}
    return repos.objectives.find(**filters) if filters else repos.objectives.get_all()


@router.post("", response_model=PIObjective, status_code=201)
def create_objective(body: PIObjectiveCreate, repos: Repos = Depends(get_repos_dep)):
    obj = PIObjective(**body.model_dump())
    return repos.objectives.save(obj)


@router.get("/{objective_id}", response_model=PIObjective)
def get_objective(objective_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, objective_id)


@router.patch("/{objective_id}", response_model=PIObjective)
def update_objective(
    objective_id: str, body: PIObjectiveUpdate, repos: Repos = Depends(get_repos_dep)
):
    obj = _get_or_404(repos, objective_id)
    updated = obj.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.objectives.save(updated)


@router.delete("/{objective_id}", status_code=204)
def delete_objective(objective_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, objective_id)
    repos.objectives.delete(objective_id)

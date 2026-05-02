from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import CapacityPlanCreate, CapacityPlanUpdate
from safe.models.capacity_plan import CapacityPlan
from safe.store.repos import Repos

router = APIRouter(prefix="/capacity-plans", tags=["Capacity Plans"])


def _get_or_404(repos: Repos, plan_id: str) -> CapacityPlan:
    plan = repos.capacity_plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Capacity plan '{plan_id}' not found")
    return plan


@router.get("", response_model=list[CapacityPlan])
def list_capacity_plans(
    pi_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    iteration_id: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    filters = {k: v for k, v in {"pi_id": pi_id, "team_id": team_id, "iteration_id": iteration_id}.items() if v is not None}
    return repos.capacity_plans.find(**filters) if filters else repos.capacity_plans.get_all()


@router.post("", response_model=CapacityPlan, status_code=201)
def create_or_update_capacity_plan(body: CapacityPlanCreate, repos: Repos = Depends(get_repos_dep)):
    existing = repos.capacity_plans.find(
        pi_id=body.pi_id, team_id=body.team_id, iteration_id=body.iteration_id
    )
    if existing:
        plan = existing[0].model_copy(update=body.model_dump())
        return repos.capacity_plans.save(plan)
    plan = CapacityPlan(**body.model_dump())
    return repos.capacity_plans.save(plan)


@router.get("/{plan_id}", response_model=CapacityPlan)
def get_capacity_plan(plan_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, plan_id)


@router.patch("/{plan_id}", response_model=CapacityPlan)
def update_capacity_plan(plan_id: str, body: CapacityPlanUpdate, repos: Repos = Depends(get_repos_dep)):
    plan = _get_or_404(repos, plan_id)
    updated = plan.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.capacity_plans.save(updated)


@router.delete("/{plan_id}", status_code=204)
def delete_capacity_plan(plan_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, plan_id)
    repos.capacity_plans.delete(plan_id)

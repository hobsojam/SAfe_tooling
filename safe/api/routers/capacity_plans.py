from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query

from safe.api.deps import ReposDep
from safe.api.schemas import CapacityPlanCreate, CapacityPlanSeed, CapacityPlanUpdate
from safe.models.capacity_plan import CapacityPlan
from safe.store.repos import Repos


def _weekdays(start: date, end: date) -> int:
    count, cur = 0, start
    while cur <= end:
        if cur.weekday() < 5:
            count += 1
        cur += timedelta(days=1)
    return count


router = APIRouter(prefix="/capacity-plans", tags=["Capacity Plans"])


def _get_or_404(repos: Repos, plan_id: str) -> CapacityPlan:
    plan = repos.capacity_plans.get(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Capacity plan '{plan_id}' not found")
    return plan


@router.get("", response_model=list[CapacityPlan])
def list_capacity_plans(
    repos: ReposDep,
    pi_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    iteration_id: str | None = Query(default=None),
):
    filters = {
        k: v
        for k, v in {"pi_id": pi_id, "team_id": team_id, "iteration_id": iteration_id}.items()
        if v is not None
    }
    return repos.capacity_plans.find(**filters) if filters else repos.capacity_plans.get_all()


@router.post("/seed", response_model=list[CapacityPlan], status_code=201)
def seed_capacity_plans(body: CapacityPlanSeed, repos: ReposDep):
    pi = repos.pis.get(body.pi_id)
    if pi is None:
        raise HTTPException(status_code=404, detail=f"PI '{body.pi_id}' not found")
    teams = repos.teams.find(art_id=pi.art_id)
    iterations = [it for it in repos.iterations.find(pi_id=body.pi_id) if not it.is_ip]
    created = []
    for team in teams:
        for iter_ in iterations:
            if repos.capacity_plans.find(pi_id=body.pi_id, team_id=team.id, iteration_id=iter_.id):
                continue
            plan = CapacityPlan(
                team_id=team.id,
                iteration_id=iter_.id,
                pi_id=body.pi_id,
                team_size=team.member_count,
                iteration_days=_weekdays(iter_.start_date, iter_.end_date),
                pto_days=0,
                overhead_pct=0.2,
            )
            repos.capacity_plans.save(plan)
            created.append(plan)
    return created


@router.post("", response_model=CapacityPlan, status_code=201)
def create_or_update_capacity_plan(body: CapacityPlanCreate, repos: ReposDep):
    existing = repos.capacity_plans.find(
        pi_id=body.pi_id, team_id=body.team_id, iteration_id=body.iteration_id
    )
    if existing:
        plan = existing[0].model_copy(update=body.model_dump())
        return repos.capacity_plans.save(plan)
    plan = CapacityPlan(**body.model_dump())
    return repos.capacity_plans.save(plan)


@router.get("/{plan_id}", response_model=CapacityPlan)
def get_capacity_plan(plan_id: str, repos: ReposDep):
    return _get_or_404(repos, plan_id)


@router.patch("/{plan_id}", response_model=CapacityPlan)
def update_capacity_plan(plan_id: str, body: CapacityPlanUpdate, repos: ReposDep):
    plan = _get_or_404(repos, plan_id)
    updated = plan.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.capacity_plans.save(updated)


@router.delete("/{plan_id}", status_code=204)
def delete_capacity_plan(plan_id: str, repos: ReposDep):
    _get_or_404(repos, plan_id)
    repos.capacity_plans.delete(plan_id)

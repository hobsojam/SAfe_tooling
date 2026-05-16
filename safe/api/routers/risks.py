from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import RiskCreate, RiskROAM, RiskUpdate
from safe.models.risk import Risk, ROAMStatus
from safe.store.repos import Repos

router = APIRouter(prefix="/risks", tags=["Risks"])


def _get_or_404(repos: Repos, risk_id: str) -> Risk:
    risk = repos.risks.get(risk_id)
    if risk is None:
        raise HTTPException(status_code=404, detail=f"Risk '{risk_id}' not found")
    return risk


@router.get("", response_model=list[Risk])
def list_risks(
    pi_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    roam_status: ROAMStatus | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    filters = {
        k: v
        for k, v in {"pi_id": pi_id, "team_id": team_id, "roam_status": roam_status}.items()
        if v is not None
    }
    return repos.risks.find(**filters) if filters else repos.risks.get_all()


@router.post("", response_model=Risk, status_code=201)
def create_risk(body: RiskCreate, repos: Repos = Depends(get_repos_dep)):
    risk = Risk(**body.model_dump())
    return repos.risks.save(risk)


@router.get("/{risk_id}", response_model=Risk)
def get_risk(risk_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, risk_id)


@router.patch("/{risk_id}", response_model=Risk)
def update_risk(risk_id: str, body: RiskUpdate, repos: Repos = Depends(get_repos_dep)):
    risk = _get_or_404(repos, risk_id)
    updated = risk.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.risks.save(updated)


@router.post("/{risk_id}/roam", response_model=Risk)
def roam_risk(risk_id: str, body: RiskROAM, repos: Repos = Depends(get_repos_dep)):
    risk = _get_or_404(repos, risk_id)
    updated = risk.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.risks.save(updated)


@router.delete("/{risk_id}", status_code=204)
def delete_risk(risk_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, risk_id)
    repos.risks.delete(risk_id)

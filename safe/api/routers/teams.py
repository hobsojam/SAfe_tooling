from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import TeamCreate, TeamUpdate
from safe.models.art import Team
from safe.store.repos import Repos

router = APIRouter(prefix="/team", tags=["Teams"])


def _get_or_404(repos: Repos, team_id: str) -> Team:
    team = repos.teams.get(team_id)
    if team is None:
        raise HTTPException(status_code=404, detail=f"Team '{team_id}' not found")
    return team


@router.get("", response_model=list[Team])
def list_teams(
    art_id: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    if art_id is not None:
        return repos.teams.find(art_id=art_id)
    return repos.teams.get_all()


@router.post("", response_model=Team, status_code=201)
def create_team(body: TeamCreate, repos: Repos = Depends(get_repos_dep)):
    if body.art_id is not None and repos.arts.get(body.art_id) is None:
        raise HTTPException(status_code=404, detail=f"ART '{body.art_id}' not found")

    team = Team(**body.model_dump())
    repos.teams.save(team)

    if body.art_id is not None:
        art = repos.arts.get(body.art_id)
        if art is not None:
            art = art.model_copy(update={"team_ids": art.team_ids + [team.id]})
            repos.arts.save(art)

    return team


@router.get("/{team_id}", response_model=Team)
def get_team(team_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, team_id)


@router.patch("/{team_id}", response_model=Team)
def update_team(team_id: str, body: TeamUpdate, repos: Repos = Depends(get_repos_dep)):
    team = _get_or_404(repos, team_id)
    updated = team.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.teams.save(updated)


@router.delete("/{team_id}", status_code=204)
def delete_team(team_id: str, repos: Repos = Depends(get_repos_dep)):
    team = _get_or_404(repos, team_id)
    repos.teams.delete(team_id)

    if team.art_id is not None:
        art = repos.arts.get(team.art_id)
        if art is not None:
            art = art.model_copy(update={"team_ids": [t for t in art.team_ids if t != team_id]})
            repos.arts.save(art)

from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import FeatureAssign, FeatureCreate, FeatureUpdate
from safe.models.backlog import Feature, FeatureStatus
from safe.store.repos import Repos

router = APIRouter(prefix="/features", tags=["Features"])


def _get_or_404(repos: Repos, feature_id: str) -> Feature:
    feature = repos.features.get(feature_id)
    if feature is None:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found")
    return feature


@router.get("", response_model=list[Feature])
def list_features(
    pi_id: str | None = Query(default=None),
    team_id: str | None = Query(default=None),
    status: FeatureStatus | None = Query(default=None),
    sort: str | None = Query(default=None, pattern="^(wsjf_desc|name_asc)$"),
    repos: Repos = Depends(get_repos_dep),
):
    filters = {
        k: v
        for k, v in {"pi_id": pi_id, "team_id": team_id, "status": status}.items()
        if v is not None
    }
    features = repos.features.find(**filters) if filters else repos.features.get_all()

    if sort == "wsjf_desc":
        features = sorted(features, key=lambda f: f.wsjf_score, reverse=True)
    elif sort == "name_asc":
        features = sorted(features, key=lambda f: f.name)

    return features


@router.post("", response_model=Feature, status_code=201)
def create_feature(body: FeatureCreate, repos: Repos = Depends(get_repos_dep)):
    feature = Feature(**body.model_dump())
    return repos.features.save(feature)


@router.get("/{feature_id}", response_model=Feature)
def get_feature(feature_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, feature_id)


@router.patch("/{feature_id}", response_model=Feature)
def update_feature(feature_id: str, body: FeatureUpdate, repos: Repos = Depends(get_repos_dep)):
    feature = _get_or_404(repos, feature_id)
    updated = feature.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.features.save(updated)


@router.post("/{feature_id}/assign", response_model=Feature)
def assign_feature(feature_id: str, body: FeatureAssign, repos: Repos = Depends(get_repos_dep)):
    feature = _get_or_404(repos, feature_id)
    if repos.teams.get(body.team_id) is None:
        raise HTTPException(status_code=404, detail=f"Team '{body.team_id}' not found")
    updated = feature.model_copy(update={"team_id": body.team_id})
    return repos.features.save(updated)


@router.delete("/{feature_id}", status_code=204)
def delete_feature(feature_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, feature_id)
    repos.features.delete(feature_id)

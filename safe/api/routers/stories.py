from fastapi import APIRouter, Depends, HTTPException, Query

from safe.api.deps import get_repos_dep
from safe.api.schemas import StoryCreate, StoryUpdate
from safe.models.backlog import Story
from safe.store.repos import Repos

router = APIRouter(prefix="/stories", tags=["Stories"])


def _get_or_404(repos: Repos, story_id: str) -> Story:
    story = repos.stories.get(story_id)
    if story is None:
        raise HTTPException(status_code=404, detail=f"Story '{story_id}' not found")
    return story


@router.get("", response_model=list[Story])
def list_stories(
    feature_id: str | None = Query(default=None),
    repos: Repos = Depends(get_repos_dep),
):
    if feature_id is not None:
        return repos.stories.find(feature_id=feature_id)
    return repos.stories.get_all()


@router.post("", response_model=Story, status_code=201)
def create_story(body: StoryCreate, repos: Repos = Depends(get_repos_dep)):
    if repos.features.get(body.feature_id) is None:
        raise HTTPException(status_code=404, detail=f"Feature '{body.feature_id}' not found")
    if repos.teams.get(body.team_id) is None:
        raise HTTPException(status_code=404, detail=f"Team '{body.team_id}' not found")
    story = Story(**body.model_dump())
    return repos.stories.save(story)


@router.get("/{story_id}", response_model=Story)
def get_story(story_id: str, repos: Repos = Depends(get_repos_dep)):
    return _get_or_404(repos, story_id)


@router.patch("/{story_id}", response_model=Story)
def update_story(story_id: str, body: StoryUpdate, repos: Repos = Depends(get_repos_dep)):
    story = _get_or_404(repos, story_id)
    updated = story.model_copy(update=body.model_dump(exclude_unset=True))
    return repos.stories.save(updated)


@router.delete("/{story_id}", status_code=204)
def delete_story(story_id: str, repos: Repos = Depends(get_repos_dep)):
    _get_or_404(repos, story_id)
    repos.stories.delete(story_id)

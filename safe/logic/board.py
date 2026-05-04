from safe.models.backlog import Feature, Story

# {team_id: {iteration_id | None: [Feature]}}
BoardGrid = dict[str, dict[str | None, list[Feature]]]


def feature_primary_iteration(feature_id: str, stories: list[Story]) -> str | None:
    """Return the iteration_id where a feature carries the most story points."""
    weight: dict[str, int] = {}
    for s in stories:
        if s.feature_id == feature_id and s.iteration_id:
            weight[s.iteration_id] = weight.get(s.iteration_id, 0) + s.points
    return max(weight, key=lambda k: weight[k]) if weight else None


def build_board(features: list[Feature], stories: list[Story]) -> BoardGrid:
    """
    Build a {team_id: {iteration_id | None: [Feature]}} grid.
    Features without a team_id are excluded.
    Prefers feature.iteration_id override; falls back to story-point majority.
    Features with neither land in the None (Unplanned) slot.
    """
    grid: BoardGrid = {}
    for feature in features:
        if feature.team_id is None:
            continue
        iter_id = feature.iteration_id or feature_primary_iteration(feature.id, stories)
        grid.setdefault(feature.team_id, {}).setdefault(iter_id, []).append(feature)
    return grid

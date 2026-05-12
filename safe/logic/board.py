from safe.models.backlog import Feature

# {team_id: {iteration_id | None: [Feature]}}
BoardGrid = dict[str, dict[str | None, list[Feature]]]


def build_board(features: list[Feature]) -> BoardGrid:
    """Build a {team_id: {iteration_id | None: [Feature]}} grid.

    Features without a team_id are excluded.
    feature.iteration_id is the sole source of truth for board placement;
    None means unplanned.
    """
    grid: BoardGrid = {}
    for feature in features:
        if feature.team_id is None:
            continue
        grid.setdefault(feature.team_id, {}).setdefault(feature.iteration_id, []).append(feature)
    return grid

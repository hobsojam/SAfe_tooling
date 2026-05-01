def team_predictability(actual_bv: int, planned_bv: int) -> float:
    if planned_bv <= 0:
        raise ValueError("planned_bv must be positive")
    return round((actual_bv / planned_bv) * 100, 1)


def art_predictability(team_results: list[tuple[int, int]]) -> float:
    """Accepts a list of (actual_bv, planned_bv) tuples, one per team."""
    total_planned = sum(p for _, p in team_results)
    total_actual = sum(a for a, _ in team_results)
    return team_predictability(total_actual, total_planned)


def predictability_rating(score: float) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"

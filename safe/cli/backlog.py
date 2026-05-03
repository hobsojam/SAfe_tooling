import typer
from rich.console import Console
from rich.table import Table

import safe.cli.state as state
from safe.store.db import get_db
from safe.store.repos import get_repos

backlog_app = typer.Typer(help="View and manage the program backlog")
console = Console()


def _repos():
    return get_repos(get_db(state.db_path) if state.db_path else None)


@backlog_app.command("show")
def backlog_show(
    pi_id: str | None = typer.Option(None, "--pi-id", help="Filter by PI"),
):
    """Show program backlog ranked by WSJF score."""
    repos = _repos()
    features = repos.features.find(pi_id=pi_id) if pi_id else repos.features.get_all()
    if not features:
        console.print("Backlog is empty.")
        return
    features.sort(key=lambda f: f.wsjf_score, reverse=True)
    table = Table("#", "Name", "Status", "CoD", "Size", "WSJF", "Stories", "Team", "PI")
    for rank, f in enumerate(features, 1):
        story_count = str(len(repos.stories.find(feature_id=f.id)))
        table.add_row(
            str(rank), f.name, f.status.value,
            str(f.cost_of_delay), str(f.job_size), str(f.wsjf_score),
            story_count, f.team_id or "-", f.pi_id or "-",
        )
    console.print(table)

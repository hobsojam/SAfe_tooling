import typer
from rich.console import Console
from rich.table import Table

import safe.cli.state as state
from safe.models.art import ART
from safe.store.db import get_db
from safe.store.repos import get_repos

art_app = typer.Typer(help="Manage Agile Release Trains")
console = Console()


def _repos():
    return get_repos(get_db(state.db_path) if state.db_path else None)


@art_app.command("create")
def art_create(
    name: str = typer.Option(..., "--name", "-n", help="ART name"),
):
    """Create a new Agile Release Train."""
    repos = _repos()
    art = ART(name=name)
    repos.arts.save(art)
    console.print(f"Created ART [bold]{art.name}[/bold] (id: {art.id})")


@art_app.command("show")
def art_show(art_id: str = typer.Argument(..., help="ART id")):
    """Show ART details."""
    repos = _repos()
    art = repos.arts.get(art_id)
    if art is None:
        console.print(f"[red]Error: ART '{art_id}' not found[/red]")
        raise typer.Exit(1)
    table = Table(show_header=False, box=None)
    table.add_row("ID", art.id)
    table.add_row("Name", art.name)
    table.add_row("Teams", str(len(art.team_ids)))
    console.print(table)


@art_app.command("list")
def art_list():
    """List all ARTs."""
    repos = _repos()
    arts = repos.arts.get_all()
    if not arts:
        console.print("No ARTs found.")
        return
    table = Table("ID", "Name", "Teams")
    for art in arts:
        table.add_row(art.id, art.name, str(len(art.team_ids)))
    console.print(table)

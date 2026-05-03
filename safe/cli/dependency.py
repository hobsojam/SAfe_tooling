from datetime import date

import typer
from rich.console import Console
from rich.table import Table

import safe.cli.state as state
from safe.models.dependency import Dependency, DependencyStatus
from safe.store.db import get_db
from safe.store.repos import get_repos

dependency_app = typer.Typer(help="Manage cross-team Dependencies")
console = Console()

_STATUS_COLOUR = {
    DependencyStatus.IDENTIFIED: "red",
    DependencyStatus.OWNED: "yellow",
    DependencyStatus.ACCEPTED: "bright_yellow",
    DependencyStatus.MITIGATED: "cyan",
    DependencyStatus.RESOLVED: "green",
}


def _repos():
    return get_repos(get_db(state.db_path) if state.db_path else None)


@dependency_app.command("add")
def dependency_add(
    description: str = typer.Option(..., "--description", "-d", help="Dependency description"),
    pi_id: str = typer.Option(..., "--pi-id", help="PI id"),
    from_team_id: str = typer.Option(..., "--from-team-id", help="Team that has the dependency"),
    to_team_id: str = typer.Option(
        ..., "--to-team-id", help="Team that must fulfil the dependency"
    ),
    feature_id: str | None = typer.Option(None, "--feature-id", help="Related feature id"),
    iteration_id: str | None = typer.Option(None, "--iteration-id", help="Iteration needed by"),
    owner: str | None = typer.Option(None, "--owner", help="Dependency owner name"),
    needed_by_date: str | None = typer.Option(None, "--needed-by", help="Date needed (YYYY-MM-DD)"),
):
    """Add a cross-team dependency for a PI."""
    repos = _repos()
    if repos.pis.get(pi_id) is None:
        console.print(f"[red]Error: PI '{pi_id}' not found[/red]")
        raise typer.Exit(1)
    if repos.teams.get(from_team_id) is None:
        console.print(f"[red]Error: Team '{from_team_id}' not found[/red]")
        raise typer.Exit(1)
    if repos.teams.get(to_team_id) is None:
        console.print(f"[red]Error: Team '{to_team_id}' not found[/red]")
        raise typer.Exit(1)
    parsed_needed_by: date | None = None
    if needed_by_date is not None:
        try:
            parsed_needed_by = date.fromisoformat(needed_by_date)
        except ValueError:
            console.print(f"[red]Error: Invalid date '{needed_by_date}' — use YYYY-MM-DD[/red]")
            raise typer.Exit(1) from None
    dep = Dependency(
        description=description,
        pi_id=pi_id,
        from_team_id=from_team_id,
        to_team_id=to_team_id,
        feature_id=feature_id,
        iteration_id=iteration_id,
        owner=owner,
        needed_by_date=parsed_needed_by,
    )
    repos.dependencies.save(dep)
    console.print(f"Added dependency (status: identified, id: {dep.id})")


@dependency_app.command("list")
def dependency_list(
    pi_id: str | None = typer.Option(None, "--pi-id", help="Filter by PI"),
    from_team_id: str | None = typer.Option(None, "--from-team-id", help="Filter by from-team"),
    to_team_id: str | None = typer.Option(None, "--to-team-id", help="Filter by to-team"),
    status: DependencyStatus | None = typer.Option(None, "--status", help="Filter by status"),
):
    """List dependencies, optionally filtered by PI, team, or status."""
    repos = _repos()
    deps = repos.dependencies.find(pi_id=pi_id) if pi_id else repos.dependencies.get_all()
    if from_team_id:
        deps = [d for d in deps if d.from_team_id == from_team_id]
    if to_team_id:
        deps = [d for d in deps if d.to_team_id == to_team_id]
    if status:
        deps = [d for d in deps if d.status == status]
    if not deps:
        console.print("No dependencies found.")
        return
    table = Table("ID", "Description", "PI", "From", "To", "Status", "Owner", "Needed By")
    for d in deps:
        from_team = repos.teams.get(d.from_team_id)
        to_team = repos.teams.get(d.to_team_id)
        colour = _STATUS_COLOUR.get(d.status, "white")
        table.add_row(
            d.id,
            d.description[:50] + ("…" if len(d.description) > 50 else ""),
            d.pi_id,
            from_team.name if from_team else d.from_team_id,
            to_team.name if to_team else d.to_team_id,
            f"[{colour}]{d.status}[/{colour}]",
            d.owner or "-",
            str(d.needed_by_date) if d.needed_by_date else "-",
        )
    console.print(table)


@dependency_app.command("show")
def dependency_show(dep_id: str = typer.Argument(..., help="Dependency id")):
    """Show full details of a dependency."""
    repos = _repos()
    dep = repos.dependencies.get(dep_id)
    if dep is None:
        console.print(f"[red]Error: Dependency '{dep_id}' not found[/red]")
        raise typer.Exit(1)
    from_team = repos.teams.get(dep.from_team_id)
    to_team = repos.teams.get(dep.to_team_id)
    colour = _STATUS_COLOUR.get(dep.status, "white")
    console.print(f"ID          : {dep.id}")
    console.print(f"Description : {dep.description}")
    console.print(f"PI          : {dep.pi_id}")
    console.print(f"From Team   : {from_team.name if from_team else dep.from_team_id}")
    console.print(f"To Team     : {to_team.name if to_team else dep.to_team_id}")
    console.print(f"Feature     : {dep.feature_id or '-'}")
    console.print(f"Iteration   : {dep.iteration_id or '-'}")
    console.print(f"Status      : [{colour}]{dep.status}[/{colour}]")
    console.print(f"Owner       : {dep.owner or '-'}")
    console.print(f"Raised      : {dep.raised_date}")
    console.print(f"Needed By   : {dep.needed_by_date or '-'}")
    if dep.resolution_notes:
        console.print(f"Notes       : {dep.resolution_notes}")


@dependency_app.command("roam")
def dependency_roam(
    dep_id: str = typer.Argument(..., help="Dependency id"),
    status: DependencyStatus = typer.Option(..., "--status", "-s", help="New status"),
    owner: str | None = typer.Option(None, "--owner", help="Dependency owner name"),
    notes: str | None = typer.Option(None, "--notes", "-n", help="Resolution notes"),
):
    """Update the status (and optionally owner/notes) for a dependency."""
    repos = _repos()
    dep = repos.dependencies.get(dep_id)
    if dep is None:
        console.print(f"[red]Error: Dependency '{dep_id}' not found[/red]")
        raise typer.Exit(1)
    updates: dict = {"status": status}
    if owner is not None:
        updates["owner"] = owner
    if notes is not None:
        updates["resolution_notes"] = notes
    updated = dep.model_copy(update=updates)
    repos.dependencies.save(updated)
    colour = _STATUS_COLOUR.get(status, "white")
    console.print(f"Dependency {dep_id} → [{colour}]{status}[/{colour}]")


@dependency_app.command("delete")
def dependency_delete(dep_id: str = typer.Argument(..., help="Dependency id")):
    """Delete a dependency."""
    repos = _repos()
    dep = repos.dependencies.get(dep_id)
    if dep is None:
        console.print(f"[red]Error: Dependency '{dep_id}' not found[/red]")
        raise typer.Exit(1)
    repos.dependencies.delete(dep_id)
    console.print(f"Deleted dependency [bold]{dep_id}[/bold]")

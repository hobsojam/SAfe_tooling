from pathlib import Path

import typer
from rich.console import Console

import safe.cli.state as state
from safe.cli.art import art_app
from safe.cli.backlog import backlog_app
from safe.cli.capacity import capacity_app
from safe.cli.feature import feature_app, feature_rank
from safe.cli.objective import objective_app
from safe.cli.risk import risk_app
from safe.cli.pi import pi_app
from safe.cli.story import story_app
from safe.cli.team import team_app
from safe.logic.wsjf import cost_of_delay, wsjf

app = typer.Typer(name="safe", help="SAFe PI Planning tools", no_args_is_help=True)
console = Console()

wsjf_app = typer.Typer(help="WSJF scoring and backlog prioritization")

app.add_typer(art_app, name="art")
app.add_typer(team_app, name="team")
app.add_typer(pi_app, name="pi")
app.add_typer(feature_app, name="feature")
app.add_typer(story_app, name="story")
app.add_typer(backlog_app, name="backlog")
app.add_typer(wsjf_app, name="wsjf")
app.add_typer(capacity_app, name="capacity")
app.add_typer(objective_app, name="objective")
app.add_typer(risk_app, name="risk")


@app.callback()
def main_callback(
    db_path: Path | None = typer.Option(
        None, "--db-path", help="Path to database file (default: ~/.safe_tooling/db.json)"
    ),
):
    if db_path is not None:
        state.db_path = db_path


wsjf_app.command("rank")(feature_rank)


@wsjf_app.command("score")
def wsjf_score(
    user_value: int = typer.Option(..., "--user-value", "-u", help="User/Business Value (1-10)"),
    time_criticality: int = typer.Option(..., "--time-crit", "-t", help="Time Criticality (1-10)"),
    risk_reduction: int = typer.Option(
        ..., "--risk-reduction", "-r", help="Risk Reduction / OE (1-10)"
    ),
    job_size: int = typer.Option(..., "--job-size", "-j", help="Job Size (1-13)"),
):
    """Calculate WSJF score for a single Feature."""
    cod = cost_of_delay(user_value, time_criticality, risk_reduction)
    score = wsjf(user_value, time_criticality, risk_reduction, job_size)
    console.print(f"Cost of Delay : [bold]{cod}[/bold]")
    console.print(f"WSJF Score    : [bold green]{score}[/bold green]")


if __name__ == "__main__":
    app()

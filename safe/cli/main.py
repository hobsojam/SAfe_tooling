from pathlib import Path

import typer
from rich.console import Console

import safe.cli.state as state
from safe.cli.art import art_app
from safe.cli.team import team_app
from safe.cli.pi import pi_app
from safe.cli.feature import feature_app, feature_rank
from safe.cli.story import story_app
from safe.cli.backlog import backlog_app
from safe.logic.wsjf import wsjf, cost_of_delay
from safe.logic.capacity import available_capacity

app = typer.Typer(name="safe", help="SAFe PI Planning tools", no_args_is_help=True)
console = Console()

wsjf_app = typer.Typer(help="WSJF scoring and backlog prioritization")
capacity_app = typer.Typer(help="Team capacity planning")

app.add_typer(art_app, name="art")
app.add_typer(team_app, name="team")
app.add_typer(pi_app, name="pi")
app.add_typer(feature_app, name="feature")
app.add_typer(story_app, name="story")
app.add_typer(backlog_app, name="backlog")
app.add_typer(wsjf_app, name="wsjf")
app.add_typer(capacity_app, name="capacity")


@app.callback()
def main_callback(
    db_path: Path | None = typer.Option(None, "--db-path", help="Path to database file (default: ~/.safe_tooling/db.json)"),
):
    if db_path is not None:
        state.db_path = db_path


wsjf_app.command("rank")(feature_rank)


@wsjf_app.command("score")
def wsjf_score(
    user_value: int = typer.Option(..., "--user-value", "-u", help="User/Business Value (1-10)"),
    time_criticality: int = typer.Option(..., "--time-crit", "-t", help="Time Criticality (1-10)"),
    risk_reduction: int = typer.Option(..., "--risk-reduction", "-r", help="Risk Reduction / OE (1-10)"),
    job_size: int = typer.Option(..., "--job-size", "-j", help="Job Size (1-13)"),
):
    """Calculate WSJF score for a single Feature."""
    cod = cost_of_delay(user_value, time_criticality, risk_reduction)
    score = wsjf(user_value, time_criticality, risk_reduction, job_size)
    console.print(f"Cost of Delay : [bold]{cod}[/bold]")
    console.print(f"WSJF Score    : [bold green]{score}[/bold green]")


@capacity_app.command("calc")
def capacity_calc(
    team_size: int = typer.Option(..., "--team-size", "-n", help="Number of team members"),
    iteration_days: int = typer.Option(10, "--days", "-d", help="Working days per iteration"),
    pto_days: float = typer.Option(0.0, "--pto", help="Total PTO days across team"),
    overhead_pct: float = typer.Option(0.2, "--overhead", help="Overhead fraction (default 0.20)"),
):
    """Calculate available team capacity for an iteration."""
    cap = available_capacity(team_size, iteration_days, pto_days, overhead_pct)
    console.print(f"Available Capacity : [bold green]{cap}[/bold green] person-days")


if __name__ == "__main__":
    app()

import typer
from rich.console import Console

app = typer.Typer(name="safe", help="SAFe PI Planning tools", no_args_is_help=True)
console = Console()

wsjf_app = typer.Typer(help="WSJF scoring and backlog prioritization")
capacity_app = typer.Typer(help="Team capacity planning")
pi_app = typer.Typer(help="PI objectives and predictability")

app.add_typer(wsjf_app, name="wsjf")
app.add_typer(capacity_app, name="capacity")
app.add_typer(pi_app, name="pi")


@wsjf_app.command("score")
def wsjf_score(
    user_value: int = typer.Option(..., "--user-value", "-u", help="User/Business Value (1-10)"),
    time_criticality: int = typer.Option(..., "--time-crit", "-t", help="Time Criticality (1-10)"),
    risk_reduction: int = typer.Option(..., "--risk-reduction", "-r", help="Risk Reduction / OE (1-10)"),
    job_size: int = typer.Option(..., "--job-size", "-j", help="Job Size (1-13)"),
):
    """Calculate WSJF score for a single Feature."""
    from safe.logic.wsjf import wsjf, cost_of_delay
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
    from safe.logic.capacity import available_capacity, capacity_warning
    cap = available_capacity(team_size, iteration_days, pto_days, overhead_pct)
    console.print(f"Available Capacity : [bold green]{cap}[/bold green] person-days")


@pi_app.command("predictability")
def pi_predictability(
    planned: list[int] = typer.Option(..., "--planned", "-p", help="Planned BV per team (repeat flag)"),
    actual: list[int] = typer.Option(..., "--actual", "-a", help="Actual BV per team (repeat flag)"),
):
    """Calculate ART PI Predictability."""
    from safe.logic.predictability import art_predictability, predictability_rating
    if len(planned) != len(actual):
        console.print("[red]Error: --planned and --actual must be provided the same number of times[/red]")
        raise typer.Exit(1)
    score = art_predictability(list(zip(actual, planned)))
    rating = predictability_rating(score)
    color = {"green": "green", "yellow": "yellow", "red": "red"}[rating]
    console.print(f"ART Predictability : [bold {color}]{score}%[/bold {color}]")


if __name__ == "__main__":
    app()

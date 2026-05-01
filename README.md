# SAFe Tooling

CLI tools for Scaled Agile Framework (SAFe) PI Planning.

## Install

Requires Python 3.11+.

```bash
pip install -e ".[dev]"
```

## What's implemented

| Tool | Status | Commands |
|------|--------|---------|
| WSJF Calculator (stateless) | Working | `safe wsjf score` |
| Capacity Planner (stateless) | Working | `safe capacity calc` |
| PI Predictability (stateless) | Working | `safe pi predictability` |
| Persistence layer | Working | — |
| ART / Team / PI setup | Planned | `safe art`, `safe team`, `safe pi` |
| Program Backlog Manager | Planned | `safe feature`, `safe backlog` |
| Capacity Planner (stateful) | Planned | `safe capacity set/show` |
| PI Objectives Tracker | Planned | `safe objective` |
| Risk Register | Planned | `safe risk` |
| Dependency Mapper | Planned | `safe dependency` |
| PI Board | Planned | `safe board` |

## Usage

### WSJF Score

Calculate a Weighted Shortest Job First score for a Feature:

```bash
safe wsjf score --user-value 8 --time-crit 5 --risk-reduction 3 --job-size 4
# Cost of Delay : 16
# WSJF Score    : 4.0
```

### Capacity Planning

Calculate available team capacity for an iteration:

```bash
safe capacity calc --team-size 7 --days 10 --pto 3 --overhead 0.2
# Available Capacity : 41.6 person-days
```

### PI Predictability

Calculate ART predictability at end of PI. Repeat `--planned` and `--actual` once per team:

```bash
safe pi predictability --planned 10 --planned 8 --actual 9 --actual 7
# ART Predictability : 84.4%
```

## Run Tests

```bash
pytest
# or with coverage
pytest --cov=safe
```

## Project Layout

```
safe/
  models/       Pydantic models (ART, Team, PI, Feature, Story, ...)
  logic/        Pure business logic (WSJF, capacity, predictability)
  cli/          Typer CLI commands
  store/        TinyDB persistence (Repository[T], get_repos())
tests/          pytest test suite
pyproject.toml
```

Data is stored locally at `~/.safe_tooling/db.json`.

## Development

See `CLAUDE.md` for full domain vocabulary, entity relationships, technical conventions, and the phased build plan.

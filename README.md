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
| ART / Team setup | Working | `safe art`, `safe team` |
| PI / Iteration setup | Working | `safe pi`, `safe pi iteration` |
| HTTP API (FastAPI) | Working | `safe-api` / `podman compose up` |
| Program Backlog Manager | Planned | `safe feature`, `safe backlog` |
| Capacity Planner (stateful) | Planned | `safe capacity set/show` |
| PI Objectives Tracker | Planned | `safe objective` |
| Risk Register | Planned | `safe risk` |
| Dependency Mapper | Planned | `safe dependency` |
| PI Board | Planned | `safe board` |

## Usage

All stateful commands accept `--db-path PATH` to override the default database location (`~/.safe_tooling/db.json`).

### ART setup

```bash
safe art create --name "Platform ART"
# Created ART Platform ART (id: abc-123)

safe art list
safe art show <id>
```

### Team setup

```bash
safe team create --name "Alpha" --members 6 --art-id <art-id>
# Created team Alpha (id: def-456)

safe team list
safe team list --art-id <art-id>   # filter by ART
safe team show <id>
safe team delete <id>
```

### PI lifecycle

```bash
safe pi create --name "PI 2026.1" --art-id <art-id> --start 2026-01-05 --end 2026-03-27
safe pi list --art-id <art-id>
safe pi activate <id>   # planning → active (one active PI per ART enforced)
safe pi close <id>      # active → closed
safe pi show <id>
```

### Iterations

```bash
safe pi iteration add --pi-id <pi-id> --number 1 --start 2026-01-05 --end 2026-01-16
safe pi iteration add --pi-id <pi-id> --number 5 --start 2026-03-16 --end 2026-03-27 --ip
safe pi iteration list --pi-id <pi-id>
safe pi iteration delete <id>
```

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

## HTTP API

The full domain is also exposed as a REST API via FastAPI.

### Run locally

```bash
safe-api
# Uvicorn running on http://127.0.0.1:8000
```

Interactive docs at `http://127.0.0.1:8000/docs`.

The DB path defaults to `~/.safe_tooling/db.json` (same as the CLI). Override with:

```bash
SAFE_DB_PATH=/path/to/db.json safe-api
```

### Run with Podman

```bash
podman compose up -d --build
```

API available at `http://127.0.0.1:8000/docs`.

> **Note:** Open `http://127.0.0.1:8000` (explicit IPv4) rather than `http://localhost:8000`
> on Windows with Podman — WSL2's IPv6 forwarding causes a connection reset with `localhost`.

Data is stored in a named Podman volume (`safe_data`) and persists across restarts.
To wipe it: `podman compose down -v`.

To share data between the CLI and the container, replace the named volume with a bind mount
in `docker-compose.yml`:

```yaml
volumes:
  - ~/.safe_tooling:/data
```

### API endpoints

All resources support standard CRUD. Key endpoints:

| Method | Path | Description |
|--------|------|-------------|
| `GET/POST` | `/art` | List / create ARTs |
| `GET/POST` | `/team` | List / create Teams |
| `GET/POST` | `/pi` | List / create PIs |
| `POST` | `/pi/{id}/activate` | Transition PI planning → active |
| `POST` | `/pi/{id}/close` | Transition PI active → closed |
| `GET/POST` | `/iterations` | List (requires `?pi_id`) / create Iterations |
| `GET/POST` | `/features` | List (supports `?sort=wsjf_desc`) / create Features |
| `POST` | `/features/{id}/assign` | Assign feature to a team |
| `GET/POST` | `/stories` | List / create Stories |
| `GET/POST` | `/objectives` | List / create PI Objectives |
| `GET/POST` | `/risks` | List / create Risks |
| `POST` | `/risks/{id}/roam` | Set ROAM status on a Risk |
| `GET/POST` | `/dependencies` | List / create Dependencies |
| `POST` | `/dependencies/{id}/roam` | Set status on a Dependency |
| `GET/POST` | `/capacity-plans` | List / upsert Capacity Plans |
| `POST` | `/compute/predictability` | Stateless ART predictability calculation |

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
  cli/
    main.py     Root Typer app; wsjf score, capacity calc; --db-path global option
    state.py    Shared CLI state (db_path)
    art.py      safe art commands
    team.py     safe team commands
    pi.py       safe pi and safe pi iteration commands
  api/
    main.py     FastAPI app; lifespan; router registration; run() entry point
    deps.py     get_repos_dep() Depends factory; DB lifecycle via lifespan
    schemas.py  Create/Update/action request body schemas
    routers/    One file per resource (arts, teams, pi, iterations, features, ...)
  store/        TinyDB persistence (Repository[T], get_repos())
tests/          pytest test suite (CLI + API)
Dockerfile
docker-compose.yml
pyproject.toml
```

Data is stored locally at `~/.safe_tooling/db.json`.

## Development

See `CLAUDE.md` for full domain vocabulary, entity relationships, technical conventions, and the phased build plan.

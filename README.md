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
| Capacity Planner | Working | `safe capacity calc/set/show/export` |
| PI Predictability (stateless) | Working | `safe pi predictability` |
| ART / Team setup | Working | `safe art`, `safe team` |
| PI / Iteration setup | Working | `safe pi`, `safe pi iteration` |
| HTTP API (FastAPI) | Working | `safe-api` / `podman compose up` |
| Program Backlog Manager | Working | `safe feature`, `safe story`, `safe backlog`, `safe wsjf rank` |
| PI Objectives Tracker | Working | `safe objective` |
| Risk Register | Working | `safe risk add/list/show/roam/delete` |
| Dependency Mapper | Planned | `safe dependency` |
| PI Board | Planned | `safe board` |
| Web Frontend | Planned | React SPA |

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

### Program Backlog Manager

```bash
# Add a feature (WSJF fields required)
safe feature add --name "Auth Service" \
  --user-value 8 --time-crit 5 --risk-reduction 3 --job-size 4 \
  --pi-id <pi-id>

# List all features
safe feature list
safe feature list --pi-id <pi-id> --status implementing

# WSJF-ranked backlog view
safe feature rank
safe wsjf rank            # alias for feature rank
safe backlog show         # ranked view with story counts

# Update a feature
safe feature update <id> --status implementing
safe feature assign <id> --team-id <team-id>

# Delete (also removes child stories)
safe feature delete <id>
```

### Stories

```bash
# Add a story to a feature
safe story add --name "Login flow" --feature-id <fid> --team-id <tid> --points 3
safe story add --name "Token refresh" --feature-id <fid> --team-id <tid> --points 2 \
  --iteration-id <iter-id>

# List stories
safe story list
safe story list --feature-id <fid>
safe story list --team-id <tid>
safe story list --iteration-id <iter-id>

# Update
safe story update <id> --status in_progress
safe story update <id> --points 5 --iteration-id <iter-id>

safe story delete <id>
```

### WSJF Score (stateless)

Calculate a Weighted Shortest Job First score for a single feature:

```bash
safe wsjf score --user-value 8 --time-crit 5 --risk-reduction 3 --job-size 4
# Cost of Delay : 16
# WSJF Score    : 4.0
```

### Capacity Planning

```bash
# Stateless calculation
safe capacity calc --team-size 7 --days 10 --pto 3 --overhead 0.2
# Available Capacity : 41.6 person-days

# Save a capacity plan for a team/iteration (upserts if one already exists)
safe capacity set --pi-id <pi-id> --team-id <tid> --iteration-id <iter-id> \
  --team-size 7 --pto 2 --overhead 0.2

# Show plans (with load % when stories are assigned to the iteration)
safe capacity show
safe capacity show --pi-id <pi-id>
safe capacity show --team-id <tid>

# Export to CSV for sharing
safe capacity export --pi-id <pi-id> --output capacity.csv
```

### PI Objectives

```bash
# Add a committed objective
safe objective add --description "Deliver auth service" \
  --team-id <tid> --pi-id <pi-id> --planned-bv 8

# Add a stretch objective
safe objective add --description "Add SSO support" \
  --team-id <tid> --pi-id <pi-id> --planned-bv 5 --stretch

# List objectives
safe objective list
safe objective list --pi-id <pi-id>
safe objective list --team-id <tid>

# Record actual business value at end of PI (for predictability)
safe objective score <id> --actual-bv 7

# Update or delete
safe objective update <id> --planned-bv 9
safe objective delete <id>
```

### Risk Register

```bash
# Add a risk (unroamed by default)
safe risk add --description "Auth service unavailable" --pi-id <pi-id>
safe risk add --description "Infra dependency missing" --pi-id <pi-id> \
  --team-id <tid> --owner "Alice"

# List all risks for a PI
safe risk list
safe risk list --pi-id <pi-id>
safe risk list --status unroamed      # highlight risks not yet dispositioned
safe risk list --team-id <tid>

# Show full detail for one risk
safe risk show <id>

# ROAM the risk (Resolved / Owned / Accepted / Mitigated)
safe risk roam <id> --status owned --owner "Bob"
safe risk roam <id> --status mitigated --notes "Added circuit breaker"
safe risk roam <id> --status resolved

# Delete
safe risk delete <id>
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
    main.py     Root Typer app; wsjf score/rank, capacity calc; --db-path global option
    state.py    Shared CLI state (db_path)
    art.py      safe art commands
    team.py     safe team commands
    pi.py       safe pi and safe pi iteration commands
    feature.py  safe feature commands (add/show/list/rank/update/assign/delete)
    story.py    safe story commands (add/list/update/delete)
    backlog.py  safe backlog show
    objective.py safe objective commands
    risk.py     safe risk commands (add/list/show/roam/delete)
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

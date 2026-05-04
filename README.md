# SAFe Tooling

A local PI Planning platform for Scaled Agile Framework (SAFe) teams. Manage your ART's Program Increments through a web interface, a REST API, or a terminal CLI — all backed by a single JSON store at `~/.safe_tooling/db.json`.

## What it does

| Domain | Capabilities |
|--------|-------------|
| **ART & Teams** | Define your Agile Release Train and teams |
| **Program Increments** | Create PIs, manage their lifecycle (planning → active → closed), add iterations |
| **Program Backlog** | Track features with WSJF scoring (Cost of Delay / Job Size), rank by priority |
| **Capacity Planning** | Set team capacity per iteration, track story point load % |
| **PI Objectives** | Record committed and stretch objectives with business value scoring |
| **Risk Register** | Log risks and ROAM them (Resolved / Owned / Accepted / Mitigated) |
| **Dependencies** | Map cross-team dependencies and track their resolution |
| **Program Board** | Visual teams × iterations board with feature placement and dependency overlay |
| **Predictability** | Calculate ART PI predictability from planned vs. actual business value |

## Three interfaces

| Interface | Best for | How to start |
|-----------|----------|-------------|
| **Web UI** | Browsing and reviewing PI data | `SAFE_SEED_DEV=1 safe-api` + `cd frontend && npm run dev` |
| **REST API** | Integrations and scripting | `safe-api` → `http://127.0.0.1:8000/docs` |
| **CLI** | Creating and updating records | `safe --help` |

---

## Quick start

### Requirements

- Python 3.11+
- Node.js 20+ (web UI only)

### Install

```bash
pip install -e ".[dev]"
```

### Option A — Web UI + API (recommended)

Open **two terminal windows** in the project root.

**Terminal 1 — API server:**
```bash
SAFE_SEED_DEV=1 safe-api
# Starts on http://127.0.0.1:8000
# Interactive docs: http://127.0.0.1:8000/docs
# SAFE_SEED_DEV=1 populates the database with sample data on first run
# Windows PowerShell: $env:SAFE_SEED_DEV = "1"; safe-api
```

**Terminal 2 — Frontend dev server:**
```bash
cd frontend
npm install   # first time only
npm run dev
# Starts on http://localhost:5173
```

Open **http://localhost:5173** in your browser. Select a PI from the sidebar to see the Board, Backlog, Risks, and Dependencies pages.

> The Vite dev server proxies `/api/*` to FastAPI on port 8000 — no CORS configuration needed.

#### Seed data for manual testing

The API includes a built-in dev seed that populates a realistic PI (two teams, four features, ten stories, risks, and dependencies). Enable it by setting `SAFE_SEED_DEV=1` when starting the API server:

**Linux / macOS:**
```bash
SAFE_SEED_DEV=1 safe-api
```

**Windows PowerShell:**
```powershell
$env:SAFE_SEED_DEV = "1"; safe-api
```

The seed only runs when the database is empty, so it is safe to set on every startup. Once any ART exists the seed is skipped.

> **Without this flag the database starts empty and the PI dropdown in the web UI will show no options.**

### Option B — CLI only

```bash
safe --help
```

All commands accept `--db-path PATH` to use a custom database file instead of `~/.safe_tooling/db.json`.

### Option C — Docker (API + frontend together)

```bash
podman compose up -d --build
# API:      http://127.0.0.1:8000
# Frontend: http://127.0.0.1:3000
```

> On Windows with Podman, use `127.0.0.1` not `localhost` — WSL2's IPv6 forwarding causes a connection reset with `localhost`.

---

## Web frontend

The React SPA provides read-only views across all four key PI artifacts for a selected PI.

| Page | Route | Description |
|------|-------|-------------|
| **Board** | `/pi/:id/board` | Program Board — feature cards placed in team × iteration grid |
| **Backlog** | `/pi/:id/backlog` | WSJF-ranked feature list |
| **Risks** | `/pi/:id/risks` | ROAM risk register with unroamed count callout |
| **Dependencies** | `/pi/:id/dependencies` | Cross-team dependency tracker with unresolved count |

Built with Vite, React 18, TypeScript, Tailwind CSS v4, TanStack Query, and React Router.

---

## REST API

Full CRUD for every domain entity, exposed via FastAPI.

```bash
safe-api                             # starts on http://127.0.0.1:8000
SAFE_DB_PATH=/path/to/db.json safe-api   # custom DB location
```

Interactive docs: **http://127.0.0.1:8000/docs**

### Key endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET/POST` | `/art` | ARTs |
| `GET/POST` | `/team` | Teams |
| `GET/POST` | `/pi` | PIs |
| `POST` | `/pi/{id}/activate` | planning → active |
| `POST` | `/pi/{id}/close` | active → closed |
| `GET/POST` | `/iterations` | Iterations (`?pi_id` required for list) |
| `GET/POST` | `/features` | Features (`?sort=wsjf_desc`, `?pi_id`, `?team_id`) |
| `POST` | `/features/{id}/assign` | Assign feature to a team |
| `GET/POST` | `/stories` | Stories |
| `GET/POST` | `/objectives` | PI Objectives |
| `GET/POST` | `/risks` | Risks |
| `POST` | `/risks/{id}/roam` | Set ROAM status |
| `GET/POST` | `/dependencies` | Dependencies |
| `POST` | `/dependencies/{id}/roam` | Set dependency status |
| `GET/POST` | `/capacity-plans` | Capacity plans (upsert) |
| `POST` | `/compute/predictability` | Stateless ART predictability |

---

## CLI reference

The CLI is the primary way to create and update records. The web UI and API are used to read and view.

### ART & Teams

```bash
safe art create --name "Platform ART"
safe art list
safe art show <id>

safe team create --name "Alpha" --members 6 --art-id <art-id>
safe team list
safe team list --art-id <art-id>
safe team show <id>
safe team delete <id>
```

### PI lifecycle

```bash
safe pi create --name "PI 2026.1" --art-id <art-id> --start 2026-01-05 --end 2026-03-27
safe pi activate <id>   # planning → active
safe pi close <id>      # active → closed
safe pi list
safe pi show <id>

safe pi iteration add --pi-id <pi-id> --number 1 --start 2026-01-05 --end 2026-01-16
safe pi iteration add --pi-id <pi-id> --number 5 --start 2026-03-16 --end 2026-03-27 --ip
safe pi iteration list --pi-id <pi-id>
safe pi iteration delete <id>
```

### Program Backlog

```bash
# Features
safe feature add --name "Auth Service" \
  --user-value 8 --time-crit 5 --risk-reduction 3 --job-size 4 --pi-id <pi-id>
safe feature assign <id> --team-id <team-id>
safe feature update <id> --status implementing
safe feature list --pi-id <pi-id>
safe feature rank              # WSJF-ranked view
safe backlog show              # ranked view with story counts
safe feature delete <id>

# Stories
safe story add --name "Login flow" --feature-id <fid> --team-id <tid> --points 3 \
  --iteration-id <iter-id>
safe story list --feature-id <fid>
safe story update <id> --status in_progress
safe story delete <id>

# Stateless WSJF calculator
safe wsjf score --user-value 8 --time-crit 5 --risk-reduction 3 --job-size 4
```

### Capacity planning

```bash
safe capacity set --pi-id <pi-id> --team-id <tid> --iteration-id <iter-id> \
  --team-size 7 --pto 2 --overhead 0.2
safe capacity show --pi-id <pi-id>
safe capacity export --pi-id <pi-id> --output capacity.csv

# Stateless calculation
safe capacity calc --team-size 7 --days 10 --pto 3 --overhead 0.2
```

### PI Objectives

```bash
safe objective add --description "Deliver auth service" \
  --team-id <tid> --pi-id <pi-id> --planned-bv 8
safe objective add --description "Add SSO support" \
  --team-id <tid> --pi-id <pi-id> --planned-bv 5 --stretch
safe objective score <id> --actual-bv 7   # record at end of PI
safe objective list --pi-id <pi-id>
safe objective update <id> --planned-bv 9
safe objective delete <id>

# ART predictability
safe pi predictability --planned 10 --planned 8 --actual 9 --actual 7
```

### Risk Register

```bash
safe risk add --description "Auth service unavailable" --pi-id <pi-id> \
  --team-id <tid> --owner "Alice"
safe risk list --pi-id <pi-id>
safe risk list --status unroamed
safe risk show <id>
safe risk roam <id> --status owned --owner "Bob"
safe risk roam <id> --status mitigated --notes "Added circuit breaker"
safe risk roam <id> --status resolved
safe risk delete <id>
```

### Dependencies

```bash
safe dependency add --description "Auth service API contract" \
  --pi-id <pi-id> --from-team-id <from-tid> --to-team-id <to-tid> \
  --owner "Alice" --needed-by 2026-02-14
safe dependency list --pi-id <pi-id>
safe dependency list --status identified
safe dependency show <id>
safe dependency roam <id> --status mitigated --notes "Interface agreed in Iteration 2"
safe dependency roam <id> --status resolved
safe dependency delete <id>
```

### Program Board

```bash
safe board show --pi-id <pi-id>
safe board export --pi-id <pi-id> --output board.xlsx
```

---

## Tests

```bash
pytest
pytest --cov=safe   # with coverage
```

---

## Project layout

```
frontend/           React SPA (Vite + TypeScript + Tailwind)
  src/
    api/            Typed fetch client
    components/     Layout, Badge, Spinner, EmptyState
    pages/          Board, Backlog, Risks, Dependencies
  Dockerfile        Multi-stage build → nginx
  nginx.conf        SPA routing + /api/ proxy to FastAPI
safe/
  models/           Pydantic models (ART, Team, PI, Feature, Story, ...)
  logic/            Pure business logic (WSJF, capacity, predictability, board)
  cli/              Typer CLI — one module per domain
  api/              FastAPI app — one router per domain
  store/            TinyDB persistence (Repository[T])
tests/              pytest suite — CLI and API
Dockerfile          Python API image
docker-compose.yml  API (port 8000) + frontend/nginx (port 3000)
pyproject.toml
```

Data is stored at `~/.safe_tooling/db.json`. The CLI and API share this file.

---

## Development notes

See `CLAUDE.md` for SAFe domain vocabulary, entity relationships, technical conventions, and the phased build plan.

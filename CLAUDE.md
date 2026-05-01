# SAFe Tooling — Project Context

## Purpose

This project builds tooling to support planning, tracking, and execution activities within the **Scaled Agile Framework (SAFe)**. The primary focus is on Program Increment (PI) Planning and related ceremonies/artifacts.

## SAFe Domain Vocabulary

Understand these terms precisely before implementing any feature:

| Term | Definition |
|------|-----------|
| **PI** | Program Increment — a fixed timebox (typically 8–12 weeks) containing 4–5 Iterations plus an Innovation & Planning (IP) iteration |
| **ART** | Agile Release Train — the long-lived team-of-teams that delivers value; typically 50–125 people |
| **Team** | An Agile team on the ART; 5–11 people including a Scrum Master and Product Owner |
| **Iteration** | A 2-week sprint within a PI |
| **Feature** | A service or function that fulfills a stakeholder need; sized to fit in a PI |
| **Story** | A small unit of work that fits within one Iteration, belonging to a Feature |
| **Epic** | A large initiative spanning multiple PIs; may have a Lean Business Case |
| **PI Objectives** | Business outcomes a team or ART commits to for a PI; rated by Business Value (1–10) |
| **WSJF** | Weighted Shortest Job First — prioritization formula: (CoD + ToD + RR/OE) / Job Size |
| **CoD** | Cost of Delay — value lost by not delivering; sum of User/Business Value, Time Criticality, Risk Reduction / Opportunity Enablement |
| **ROAM** | Risk disposition: Resolved, Owned, Accepted, Mitigated |
| **RTE** | Release Train Engineer — servant leader and coach for the ART |
| **Program Board** | Visual artifact mapping Features to Iterations, showing team dependencies |
| **Dependency** | A cross-team or cross-ART reliance that must be coordinated |
| **Capacity** | Available person-days per team per Iteration, accounting for PTO and overhead |
| **Load** | Estimated Story Points or hours committed by a team in an Iteration |
| **IP Iteration** | Innovation & Planning iteration at the end of a PI; not used for regular feature delivery |
| **ART Sync** | Short, regular cross-team coordination meeting during the PI |
| **Inspect & Adapt (I&A)** | End-of-PI ceremony: PI System Demo + quantitative measurement + problem-solving workshop |

## Key Formulas

```
WSJF = Cost of Delay / Job Duration (relative sizing, 1–13 scale)
Cost of Delay = User/Business Value + Time Criticality + Risk Reduction/Opportunity Enablement

Predictability = (Actual Business Value / Planned Business Value) * 100
Target: 80–100%

Team Load % = (Committed Story Points / Available Capacity) * 100
Target: ≤ 100%, warn at > 90%

Available Capacity = (Team Size × Iteration Days − PTO Days) × (1 − Overhead %)
Default overhead: 20%
```

## Entity Relationships

```
ART  1──* Team
ART  1──* PI
PI   1──* Iteration
PI   1──* Feature
PI   1──* Risk
PI   1──* PIObjective  (via Team)
PI   1──* Dependency
Team 1──* PIObjective
Team 1──* CapacityPlan  (one per Iteration)
Feature *──1 Team  (assigned team)
Feature 1──* Story
Feature 1──* Dependency  (feature_id FK)
Story  belongs to Team and Iteration
```

All relationships use ID references (never embedded objects). `PI.iteration_ids`, `Feature.story_ids`, etc. store lists of IDs; the repository layer loads related entities separately. This avoids dual-write bugs in TinyDB.

## Technology Stack

| Layer | Library | Purpose |
|-------|---------|---------|
| Language | Python 3.14 | |
| CLI | Typer (`typer[all]`) | Subcommand structure, `--help` generation |
| Data models | Pydantic v2 | Validated models with `computed_field` for derived values |
| Persistence | TinyDB | JSON-backed local store at `~/.safe_tooling/db.json` |
| Terminal output | Rich (bundled with Typer) | Colored tables, status indicators |
| Spreadsheet I/O | openpyxl | Import/export for PI Planning Excel artifacts |
| Testing | pytest + pytest-cov | |

Install: `pip install -e ".[dev]"`
Run CLI: `safe --help`

## Project Structure

```
safe/
  models/
    __init__.py          # re-exports all models — import from here
    art.py               # ART, Team
    pi.py                # PI, Iteration, PIStatus
    backlog.py           # Feature, FeatureStatus, Story, StoryStatus
    objectives.py        # PIObjective
    risk.py              # Risk, ROAMStatus
    dependency.py        # Dependency, DependencyStatus
    capacity_plan.py     # CapacityPlan
  logic/
    wsjf.py              # cost_of_delay(), wsjf(), rank_features()
    capacity.py          # available_capacity(), load_percentage(), capacity_warning()
    predictability.py    # team_predictability(), art_predictability(), predictability_rating()
  cli/
    main.py              # root Typer app; wsjf score, capacity calc, pi predictability
  store/
    db.py                # get_db(path?), close_db() — singleton TinyDB
    repository.py        # Repository[T] — generic save/get/find/delete
    repos.py             # Repos dataclass; get_repos() entry point
tests/
  test_wsjf.py
  test_capacity.py
  test_predictability.py
  test_repository.py
pyproject.toml
```

## Technical Conventions

**Models**
- All models live in `safe/models/`; import via `safe.models` (the `__init__.py`), not individual files.
- Every entity has an `id: str` field with a `uuid4` default.
- Computed fields (`wsjf_score`, `cost_of_delay`, `available_capacity`, `is_committed`) use Pydantic `@computed_field`. They are **never stored** — the repository excludes them on `save()` and they are recomputed on `model_validate()`.
- `date` fields serialise to ISO strings via `model_dump(mode="json")` and round-trip correctly through `model_validate`.

**Persistence**
- All storage goes through `Repository[T]` in `safe/store/repository.py`. No code should call `TinyDB` directly outside `store/`.
- Use `get_repos()` to obtain all repositories. Pass a `TinyDB` instance (from `get_db(tmp_path)`) in tests to avoid touching the real database.
- `save()` is an upsert keyed on `id`. Deletion of entities referenced by others should check for downstream references first.

**Logic**
- Business logic lives in pure functions in `safe/logic/`. No I/O, no TinyDB, no Rich imports.
- CLI modules (`safe/cli/`) are the only place Rich rendering happens.
- CLI commands call logic functions; logic functions accept model objects or plain scalars.

**Testing**
- Repository tests use `tmp_path` fixture to get a fresh TinyDB per test.
- Logic tests are pure unit tests with no I/O.
- CLI tests use `typer.testing.CliRunner` with a `--db-path` pointing to a tmp file.

## Build Phases

| Phase | Scope | Status |
|-------|-------|--------|
| 1 | Persistence foundation — `Repository[T]`, model extensions, new models | **Done** |
| 2 | ART / Team / PI setup commands | Not started |
| 3 | Program Backlog Manager + stateful WSJF | Not started |
| 4 | Capacity Planner (stateful) | Not started |
| 5 | PI Objectives Tracker | Not started |
| 6 | Risk Register | Not started |
| 7 | Dependency Mapper | Not started |
| 8 | PI Board (integrating view) | Not started |

## Planned CLI Command Tree

```
safe [--db-path PATH]
  ├── art       create / show / list
  ├── team      create / show / list / delete
  ├── pi        create / show / list / activate / close / predictability
  │   └── iteration  add / list / delete
  ├── feature   add / show / list / rank / update / assign / delete
  ├── wsjf      score (stateless) / rank (alias for feature rank)
  ├── backlog   show / import / export
  ├── story     add / list / update / delete
  ├── capacity  calc (stateless) / set / show / export
  ├── objective add / list / score / update / delete
  ├── risk      add / list / roam / show / delete
  ├── dependency add / list / roam / show / delete
  └── board     show / export
```

## Out of Scope

- Full ALM/project management system replacement (not Jira/Rally)
- Portfolio-level SAFe artifacts (Value Streams, Strategic Themes) unless explicitly added later
- Multi-ART coordination (single ART focus for now)
- Multi-user or shared access (local single-user tool only)

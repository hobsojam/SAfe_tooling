import csv
from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.capacity as capacity_module
import safe.cli.state as state
from safe.cli.main import app
from safe.store.db import get_db
from safe.store.repos import get_repos

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_state():
    state.db_path = None
    yield
    state.db_path = None


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "test.json"


@pytest.fixture(autouse=True)
def patch_console(monkeypatch):
    buf = StringIO()
    test_console = Console(file=buf, highlight=False, markup=False, width=200)
    monkeypatch.setattr(capacity_module, "console", test_console)
    yield buf


def invoke(db_path: Path, *args):
    return runner.invoke(app, ["--db-path", str(db_path)] + list(args))


def repos_for(db_path: Path):
    return get_repos(get_db(db_path))


def _setup(db_path):
    """Create ART → PI → Team → Iteration, return (pi_id, team_id, iter_id)."""
    invoke(db_path, "art", "create", "--name", "ART")
    art_id = repos_for(db_path).arts.get_all()[0].id
    invoke(
        db_path,
        "pi",
        "create",
        "--name",
        "PI 1",
        "--art-id",
        art_id,
        "--start",
        "2026-01-05",
        "--end",
        "2026-03-27",
    )
    pi_id = repos_for(db_path).pis.get_all()[0].id
    invoke(db_path, "team", "create", "--name", "Alpha", "--members", "6")
    team_id = repos_for(db_path).teams.get_all()[0].id
    invoke(
        db_path,
        "pi",
        "iteration",
        "add",
        "--pi-id",
        pi_id,
        "--number",
        "1",
        "--start",
        "2026-01-05",
        "--end",
        "2026-01-16",
    )
    iter_id = repos_for(db_path).iterations.get_all()[0].id
    return pi_id, team_id, iter_id


def _set_plan(db_path, pi_id, team_id, iter_id, team_size=7, extra=None):
    args = [
        "capacity",
        "set",
        "--pi-id",
        pi_id,
        "--team-id",
        team_id,
        "--iteration-id",
        iter_id,
        "--team-size",
        str(team_size),
    ]
    return invoke(db_path, *(args + (extra or [])))


class TestCapacitySet:
    def test_creates_plan(self, db_path, patch_console):
        pi_id, team_id, iter_id = _setup(db_path)
        result = _set_plan(db_path, pi_id, team_id, iter_id)
        assert result.exit_code == 0
        plans = repos_for(db_path).capacity_plans.get_all()
        assert len(plans) == 1

    def test_available_capacity_in_output(self, db_path, patch_console):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=5)
        # 5 × 10 × 0.8 = 40.0
        assert "40.0" in patch_console.getvalue()

    def test_upserts_existing(self, db_path, patch_console):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=5)
        plan_id = repos_for(db_path).capacity_plans.get_all()[0].id
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=8)
        plans = repos_for(db_path).capacity_plans.get_all()
        assert len(plans) == 1
        assert plans[0].id == plan_id
        assert plans[0].team_size == 8

    def test_unknown_pi_exits_1(self, db_path, patch_console):
        _, team_id, iter_id = _setup(db_path)
        pi_id, team_id, iter_id = _setup(db_path)
        result = invoke(
            db_path,
            "capacity",
            "set",
            "--pi-id",
            "bad",
            "--team-id",
            team_id,
            "--iteration-id",
            iter_id,
            "--team-size",
            "5",
        )
        assert result.exit_code == 1

    def test_unknown_team_exits_1(self, db_path, patch_console):
        pi_id, _, iter_id = _setup(db_path)
        result = invoke(
            db_path,
            "capacity",
            "set",
            "--pi-id",
            pi_id,
            "--team-id",
            "bad",
            "--iteration-id",
            iter_id,
            "--team-size",
            "5",
        )
        assert result.exit_code == 1

    def test_unknown_iteration_exits_1(self, db_path, patch_console):
        pi_id, team_id, _ = _setup(db_path)
        result = invoke(
            db_path,
            "capacity",
            "set",
            "--pi-id",
            pi_id,
            "--team-id",
            team_id,
            "--iteration-id",
            "bad",
            "--team-size",
            "5",
        )
        assert result.exit_code == 1


class TestCapacityShow:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "capacity", "show")
        assert "No capacity plans found" in patch_console.getvalue()

    def test_shows_plan(self, db_path, patch_console):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=6)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "capacity", "show")
        assert "Alpha" in patch_console.getvalue()

    def test_filter_by_pi(self, db_path, patch_console):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id)
        patch_console.truncate(0)
        patch_console.seek(0)
        result = invoke(db_path, "capacity", "show", "--pi-id", pi_id)
        assert result.exit_code == 0
        assert "Alpha" in patch_console.getvalue()

    def test_exit_code_success(self, db_path, patch_console):
        result = invoke(db_path, "capacity", "show")
        assert result.exit_code == 0


class TestCapacityExport:
    def test_creates_csv(self, db_path, patch_console, tmp_path):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=6)
        out = tmp_path / "cap.csv"
        result = invoke(db_path, "capacity", "export", "--pi-id", pi_id, "--output", str(out))
        assert result.exit_code == 0
        assert out.exists()

    def test_csv_has_header_and_row(self, db_path, patch_console, tmp_path):
        pi_id, team_id, iter_id = _setup(db_path)
        _set_plan(db_path, pi_id, team_id, iter_id, team_size=6)
        out = tmp_path / "cap.csv"
        invoke(db_path, "capacity", "export", "--pi-id", pi_id, "--output", str(out))
        rows = list(csv.reader(out.open()))
        assert rows[0][0] == "team"
        assert rows[1][0] == "Alpha"

    def test_unknown_pi_exits_1(self, db_path, patch_console, tmp_path):
        result = invoke(db_path, "capacity", "export", "--pi-id", "bad")
        assert result.exit_code == 1

    def test_empty_pi_reports_no_plans(self, db_path, patch_console, tmp_path):
        _setup(db_path)
        pi_id = repos_for(db_path).pis.get_all()[0].id
        invoke(db_path, "capacity", "export", "--pi-id", pi_id)
        assert "No capacity plans found" in patch_console.getvalue()

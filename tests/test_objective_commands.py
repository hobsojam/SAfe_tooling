from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.objective as objective_module
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
    monkeypatch.setattr(objective_module, "console", test_console)
    yield buf


def invoke(db_path: Path, *args):
    return runner.invoke(app, ["--db-path", str(db_path)] + list(args))


def repos_for(db_path: Path):
    return get_repos(get_db(db_path))


def _setup(db_path):
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
    return pi_id, team_id


def _add_objective(db_path, pi_id, team_id, planned_bv=8, stretch=False):
    args = [
        "objective",
        "add",
        "--description",
        "Deliver auth service",
        "--team-id",
        team_id,
        "--pi-id",
        pi_id,
        "--planned-bv",
        str(planned_bv),
    ]
    if stretch:
        args.append("--stretch")
    return invoke(db_path, *args)


class TestObjectiveAdd:
    def test_exit_code_success(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        result = _add_objective(db_path, pi_id, team_id)
        assert result.exit_code == 0

    def test_stored_in_db(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id, planned_bv=7)
        objs = repos_for(db_path).objectives.get_all()
        assert len(objs) == 1
        assert objs[0].planned_business_value == 7

    def test_committed_by_default(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        obj = repos_for(db_path).objectives.get_all()[0]
        assert obj.is_stretch is False
        assert obj.is_committed is True

    def test_stretch_flag(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id, stretch=True)
        obj = repos_for(db_path).objectives.get_all()[0]
        assert obj.is_stretch is True

    def test_unknown_team_exits_1(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        result = invoke(
            db_path,
            "objective",
            "add",
            "--description",
            "X",
            "--team-id",
            "bad",
            "--pi-id",
            pi_id,
            "--planned-bv",
            "5",
        )
        assert result.exit_code == 1

    def test_unknown_pi_exits_1(self, db_path, patch_console):
        _, team_id = _setup(db_path)
        result = invoke(
            db_path,
            "objective",
            "add",
            "--description",
            "X",
            "--team-id",
            team_id,
            "--pi-id",
            "bad",
            "--planned-bv",
            "5",
        )
        assert result.exit_code == 1


class TestObjectiveList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "objective", "list")
        assert "No objectives found" in patch_console.getvalue()

    def test_lists_objective(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "objective", "list")
        assert "Deliver auth service" in patch_console.getvalue()

    def test_filter_by_pi(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        result = invoke(db_path, "objective", "list", "--pi-id", pi_id)
        assert result.exit_code == 0

    def test_filter_by_team(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        result = invoke(db_path, "objective", "list", "--team-id", team_id)
        assert result.exit_code == 0


class TestObjectiveScore:
    def test_records_actual_bv(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id, planned_bv=8)
        obj = repos_for(db_path).objectives.get_all()[0]
        invoke(db_path, "objective", "score", obj.id, "--actual-bv", "7")
        updated = repos_for(db_path).objectives.get(obj.id)
        assert updated.actual_business_value == 7

    def test_output_shows_planned_and_actual(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id, planned_bv=8)
        obj = repos_for(db_path).objectives.get_all()[0]
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "objective", "score", obj.id, "--actual-bv", "6")
        assert "8" in patch_console.getvalue()
        assert "6" in patch_console.getvalue()

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "objective", "score", "no-such-id", "--actual-bv", "5")
        assert result.exit_code == 1


class TestObjectiveUpdate:
    def test_update_description(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        obj = repos_for(db_path).objectives.get_all()[0]
        invoke(db_path, "objective", "update", obj.id, "--description", "New goal")
        updated = repos_for(db_path).objectives.get(obj.id)
        assert updated.description == "New goal"

    def test_update_planned_bv(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id, planned_bv=5)
        obj = repos_for(db_path).objectives.get_all()[0]
        invoke(db_path, "objective", "update", obj.id, "--planned-bv", "9")
        updated = repos_for(db_path).objectives.get(obj.id)
        assert updated.planned_business_value == 9

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "objective", "update", "no-such-id", "--description", "X")
        assert result.exit_code == 1


class TestObjectiveDelete:
    def test_removes_objective(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_objective(db_path, pi_id, team_id)
        obj = repos_for(db_path).objectives.get_all()[0]
        invoke(db_path, "objective", "delete", obj.id)
        assert repos_for(db_path).objectives.get(obj.id) is None

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "objective", "delete", "no-such-id")
        assert result.exit_code == 1

from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.dependency as dependency_module
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
    monkeypatch.setattr(dependency_module, "console", test_console)
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
    invoke(db_path, "team", "create", "--name", "Beta", "--members", "5")
    teams = repos_for(db_path).teams.get_all()
    alpha_id = next(t.id for t in teams if t.name == "Alpha")
    beta_id = next(t.id for t in teams if t.name == "Beta")
    return pi_id, alpha_id, beta_id


def _add_dep(db_path, pi_id, from_team_id, to_team_id, description="Auth service integration"):
    return invoke(
        db_path,
        "dependency",
        "add",
        "--description",
        description,
        "--pi-id",
        pi_id,
        "--from-team-id",
        from_team_id,
        "--to-team-id",
        to_team_id,
    )


class TestDependencyAdd:
    def test_exit_code_success(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        result = _add_dep(db_path, pi_id, alpha_id, beta_id)
        assert result.exit_code == 0

    def test_stored_in_db(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id, description="API contract")
        deps = repos_for(db_path).dependencies.get_all()
        assert len(deps) == 1
        assert deps[0].description == "API contract"

    def test_default_status_identified(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        assert dep.status == "identified"

    def test_teams_stored_correctly(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        assert dep.from_team_id == alpha_id
        assert dep.to_team_id == beta_id

    def test_unknown_pi_exits_1(self, db_path, patch_console):
        _, alpha_id, beta_id = _setup(db_path)
        result = invoke(
            db_path,
            "dependency",
            "add",
            "--description",
            "X",
            "--pi-id",
            "bad",
            "--from-team-id",
            alpha_id,
            "--to-team-id",
            beta_id,
        )
        assert result.exit_code == 1

    def test_unknown_from_team_exits_1(self, db_path, patch_console):
        pi_id, _, beta_id = _setup(db_path)
        result = invoke(
            db_path,
            "dependency",
            "add",
            "--description",
            "X",
            "--pi-id",
            pi_id,
            "--from-team-id",
            "bad",
            "--to-team-id",
            beta_id,
        )
        assert result.exit_code == 1

    def test_unknown_to_team_exits_1(self, db_path, patch_console):
        pi_id, alpha_id, _ = _setup(db_path)
        result = invoke(
            db_path,
            "dependency",
            "add",
            "--description",
            "X",
            "--pi-id",
            pi_id,
            "--from-team-id",
            alpha_id,
            "--to-team-id",
            "bad",
        )
        assert result.exit_code == 1

    def test_invalid_date_exits_1(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        result = invoke(
            db_path,
            "dependency",
            "add",
            "--description",
            "X",
            "--pi-id",
            pi_id,
            "--from-team-id",
            alpha_id,
            "--to-team-id",
            beta_id,
            "--needed-by",
            "not-a-date",
        )
        assert result.exit_code == 1

    def test_with_needed_by_date(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        invoke(
            db_path,
            "dependency",
            "add",
            "--description",
            "X",
            "--pi-id",
            pi_id,
            "--from-team-id",
            alpha_id,
            "--to-team-id",
            beta_id,
            "--needed-by",
            "2026-02-01",
        )
        dep = repos_for(db_path).dependencies.get_all()[0]
        assert str(dep.needed_by_date) == "2026-02-01"


class TestDependencyList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "dependency", "list")
        assert "No dependencies found" in patch_console.getvalue()

    def test_lists_dependency(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id, description="Shared library")
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "dependency", "list")
        assert "Shared library" in patch_console.getvalue()

    def test_filter_by_pi(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        result = invoke(db_path, "dependency", "list", "--pi-id", pi_id)
        assert result.exit_code == 0

    def test_filter_by_from_team(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        result = invoke(db_path, "dependency", "list", "--from-team-id", alpha_id)
        assert result.exit_code == 0

    def test_filter_by_to_team(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        result = invoke(db_path, "dependency", "list", "--to-team-id", beta_id)
        assert result.exit_code == 0

    def test_filter_by_status(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        result = invoke(db_path, "dependency", "list", "--status", "identified")
        assert result.exit_code == 0

    def test_team_names_shown(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "dependency", "list")
        output = patch_console.getvalue()
        assert "Alpha" in output
        assert "Beta" in output


class TestDependencyShow:
    def test_shows_all_fields(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id, description="Platform API needed")
        dep = repos_for(db_path).dependencies.get_all()[0]
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "dependency", "show", dep.id)
        output = patch_console.getvalue()
        assert "Platform API needed" in output
        assert "identified" in output
        assert "Alpha" in output
        assert "Beta" in output

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "dependency", "show", "no-such-id")
        assert result.exit_code == 1


class TestDependencyROAM:
    def test_updates_status(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        invoke(db_path, "dependency", "roam", dep.id, "--status", "owned")
        updated = repos_for(db_path).dependencies.get(dep.id)
        assert updated.status == "owned"

    def test_sets_owner(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        invoke(db_path, "dependency", "roam", dep.id, "--status", "owned", "--owner", "Alice")
        updated = repos_for(db_path).dependencies.get(dep.id)
        assert updated.owner == "Alice"

    def test_sets_resolution_notes(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        invoke(
            db_path,
            "dependency",
            "roam",
            dep.id,
            "--status",
            "resolved",
            "--notes",
            "Contract agreed",
        )
        updated = repos_for(db_path).dependencies.get(dep.id)
        assert updated.resolution_notes == "Contract agreed"

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "dependency", "roam", "no-such-id", "--status", "resolved")
        assert result.exit_code == 1

    def test_all_statuses_accepted(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        for status in ("identified", "owned", "accepted", "mitigated", "resolved"):
            _add_dep(db_path, pi_id, alpha_id, beta_id)
            dep = repos_for(db_path).dependencies.get_all()[-1]
            result = invoke(db_path, "dependency", "roam", dep.id, "--status", status)
            assert result.exit_code == 0


class TestDependencyDelete:
    def test_removes_dependency(self, db_path, patch_console):
        pi_id, alpha_id, beta_id = _setup(db_path)
        _add_dep(db_path, pi_id, alpha_id, beta_id)
        dep = repos_for(db_path).dependencies.get_all()[0]
        invoke(db_path, "dependency", "delete", dep.id)
        assert repos_for(db_path).dependencies.get(dep.id) is None

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "dependency", "delete", "no-such-id")
        assert result.exit_code == 1

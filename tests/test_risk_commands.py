from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.risk as risk_module
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
    monkeypatch.setattr(risk_module, "console", test_console)
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


def _add_risk(db_path, pi_id, team_id=None, description="Auth service unavailable"):
    args = ["risk", "add", "--description", description, "--pi-id", pi_id]
    if team_id:
        args += ["--team-id", team_id]
    return invoke(db_path, *args)


class TestRiskAdd:
    def test_exit_code_success(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        result = _add_risk(db_path, pi_id)
        assert result.exit_code == 0

    def test_stored_in_db(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id, description="Infra risk")
        risks = repos_for(db_path).risks.get_all()
        assert len(risks) == 1
        assert risks[0].description == "Infra risk"

    def test_default_status_unroamed(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        risk = repos_for(db_path).risks.get_all()[0]
        assert risk.roam_status == "unroamed"

    def test_with_team(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_risk(db_path, pi_id, team_id=team_id)
        risk = repos_for(db_path).risks.get_all()[0]
        assert risk.team_id == team_id

    def test_unknown_pi_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "risk", "add", "--description", "X", "--pi-id", "bad")
        assert result.exit_code == 1

    def test_unknown_team_exits_1(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        result = invoke(
            db_path, "risk", "add", "--description", "X", "--pi-id", pi_id, "--team-id", "bad"
        )
        assert result.exit_code == 1


class TestRiskList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "risk", "list")
        assert "No risks found" in patch_console.getvalue()

    def test_lists_risk(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id, description="Database failure")
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "risk", "list")
        assert "Database failure" in patch_console.getvalue()

    def test_filter_by_pi(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        result = invoke(db_path, "risk", "list", "--pi-id", pi_id)
        assert result.exit_code == 0

    def test_filter_by_team(self, db_path, patch_console):
        pi_id, team_id = _setup(db_path)
        _add_risk(db_path, pi_id, team_id=team_id)
        result = invoke(db_path, "risk", "list", "--team-id", team_id)
        assert result.exit_code == 0

    def test_filter_by_status(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        result = invoke(db_path, "risk", "list", "--status", "unroamed")
        assert result.exit_code == 0


class TestRiskShow:
    def test_shows_all_fields(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id, description="Network outage risk")
        risk = repos_for(db_path).risks.get_all()[0]
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "risk", "show", risk.id)
        output = patch_console.getvalue()
        assert "Network outage risk" in output
        assert "unroamed" in output

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "risk", "show", "no-such-id")
        assert result.exit_code == 1


class TestRiskROAM:
    def test_updates_status(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        risk = repos_for(db_path).risks.get_all()[0]
        invoke(db_path, "risk", "roam", risk.id, "--status", "owned")
        updated = repos_for(db_path).risks.get(risk.id)
        assert updated.roam_status == "owned"

    def test_sets_owner(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        risk = repos_for(db_path).risks.get_all()[0]
        invoke(db_path, "risk", "roam", risk.id, "--status", "owned", "--owner", "Alice")
        updated = repos_for(db_path).risks.get(risk.id)
        assert updated.owner == "Alice"

    def test_sets_mitigation_notes(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        risk = repos_for(db_path).risks.get_all()[0]
        invoke(
            db_path, "risk", "roam", risk.id, "--status", "mitigated", "--notes", "Failover added"
        )
        updated = repos_for(db_path).risks.get(risk.id)
        assert updated.mitigation_notes == "Failover added"

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "risk", "roam", "no-such-id", "--status", "resolved")
        assert result.exit_code == 1

    def test_all_statuses_accepted(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        for status in ("owned", "accepted", "mitigated", "resolved", "unroamed"):
            _add_risk(db_path, pi_id)
            risk = repos_for(db_path).risks.get_all()[-1]
            result = invoke(db_path, "risk", "roam", risk.id, "--status", status)
            assert result.exit_code == 0


class TestRiskDelete:
    def test_removes_risk(self, db_path, patch_console):
        pi_id, _ = _setup(db_path)
        _add_risk(db_path, pi_id)
        risk = repos_for(db_path).risks.get_all()[0]
        invoke(db_path, "risk", "delete", risk.id)
        assert repos_for(db_path).risks.get(risk.id) is None

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "risk", "delete", "no-such-id")
        assert result.exit_code == 1

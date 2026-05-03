import pytest
from io import StringIO
from pathlib import Path
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.feature as feature_module
import safe.cli.state as state
from safe.cli.main import app
from safe.store.db import get_db
from safe.store.repos import get_repos

runner = CliRunner()

FEATURE_ARGS = [
    "--name", "Auth Service",
    "--user-value", "8",
    "--time-crit", "5",
    "--risk-reduction", "3",
    "--job-size", "4",
]


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
    test_console = Console(file=buf, highlight=False, markup=False)
    monkeypatch.setattr(feature_module, "console", test_console)
    yield buf


def invoke(db_path: Path, *args):
    return runner.invoke(app, ["--db-path", str(db_path)] + list(args))


def repos_for(db_path: Path):
    return get_repos(get_db(db_path))


def _add_feature(db_path, extra_args=None):
    args = ["feature", "add"] + FEATURE_ARGS + (extra_args or [])
    invoke(db_path, *args)
    return repos_for(db_path).features.get_all()[0]


class TestFeatureAdd:
    def test_exit_code_success(self, db_path, patch_console):
        result = invoke(db_path, "feature", "add", *FEATURE_ARGS)
        assert result.exit_code == 0

    def test_stored_in_db(self, db_path, patch_console):
        invoke(db_path, "feature", "add", *FEATURE_ARGS)
        features = repos_for(db_path).features.get_all()
        assert len(features) == 1
        assert features[0].name == "Auth Service"

    def test_wsjf_in_output(self, db_path, patch_console):
        invoke(db_path, "feature", "add", *FEATURE_ARGS)
        assert "WSJF" in patch_console.getvalue()

    def test_missing_required_exits_nonzero(self, db_path, patch_console):
        result = invoke(db_path, "feature", "add", "--name", "X")
        assert result.exit_code != 0

    def test_invalid_pi_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "feature", "add", *FEATURE_ARGS, "--pi-id", "no-such-pi")
        assert result.exit_code == 1
        assert "Error" in patch_console.getvalue()


class TestFeatureShow:
    def test_shows_name(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "feature", "show", f.id)
        assert "Auth Service" in patch_console.getvalue()

    def test_shows_wsjf(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "feature", "show", f.id)
        assert "WSJF" in patch_console.getvalue()

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "feature", "show", "no-such-id")
        assert result.exit_code == 1


class TestFeatureList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "feature", "list")
        assert "No features found" in patch_console.getvalue()

    def test_lists_feature(self, db_path, patch_console):
        _add_feature(db_path)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "feature", "list")
        assert "Auth Service" in patch_console.getvalue()

    def test_invalid_status_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "feature", "list", "--status", "bad-status")
        assert result.exit_code == 1


class TestFeatureRank:
    def test_ranks_by_wsjf(self, db_path, patch_console):
        invoke(db_path, "feature", "add", "--name", "Low WSJF",
               "--user-value", "1", "--time-crit", "1", "--risk-reduction", "1", "--job-size", "13")
        invoke(db_path, "feature", "add", *FEATURE_ARGS)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "feature", "rank")
        output = patch_console.getvalue()
        assert output.index("Auth Service") < output.index("Low WSJF")

    def test_empty(self, db_path, patch_console):
        invoke(db_path, "feature", "rank")
        assert "No features found" in patch_console.getvalue()


class TestFeatureUpdate:
    def test_update_name(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "feature", "update", f.id, "--name", "Renamed Feature")
        updated = repos_for(db_path).features.get(f.id)
        assert updated.name == "Renamed Feature"

    def test_update_status(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "feature", "update", f.id, "--status", "implementing")
        updated = repos_for(db_path).features.get(f.id)
        assert updated.status.value == "implementing"

    def test_invalid_status_exits_1(self, db_path, patch_console):
        f = _add_feature(db_path)
        result = invoke(db_path, "feature", "update", f.id, "--status", "bad")
        assert result.exit_code == 1

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "feature", "update", "no-such-id", "--name", "X")
        assert result.exit_code == 1


class TestFeatureAssign:
    def test_assigns_team(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "team", "create", "--name", "Alpha", "--members", "6")
        team = repos_for(db_path).teams.get_all()[0]
        result = invoke(db_path, "feature", "assign", f.id, "--team-id", team.id)
        assert result.exit_code == 0
        updated = repos_for(db_path).features.get(f.id)
        assert updated.team_id == team.id

    def test_unknown_feature_exits_1(self, db_path, patch_console):
        invoke(db_path, "team", "create", "--name", "Alpha", "--members", "6")
        team = repos_for(db_path).teams.get_all()[0]
        result = invoke(db_path, "feature", "assign", "no-such-id", "--team-id", team.id)
        assert result.exit_code == 1

    def test_unknown_team_exits_1(self, db_path, patch_console):
        f = _add_feature(db_path)
        result = invoke(db_path, "feature", "assign", f.id, "--team-id", "no-such-team")
        assert result.exit_code == 1


class TestFeatureDelete:
    def test_removes_feature(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "feature", "delete", f.id)
        assert repos_for(db_path).features.get(f.id) is None

    def test_also_removes_stories(self, db_path, patch_console):
        f = _add_feature(db_path)
        invoke(db_path, "team", "create", "--name", "Alpha", "--members", "6")
        team = repos_for(db_path).teams.get_all()[0]
        invoke(db_path, "story", "add",
               "--name", "S1", "--feature-id", f.id, "--team-id", team.id, "--points", "3")
        story = repos_for(db_path).stories.get_all()[0]
        invoke(db_path, "feature", "delete", f.id)
        assert repos_for(db_path).stories.get(story.id) is None

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "feature", "delete", "no-such-id")
        assert result.exit_code == 1

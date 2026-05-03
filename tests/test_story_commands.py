from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.state as state
import safe.cli.story as story_module
from safe.cli.main import app
from safe.store.db import get_db
from safe.store.repos import get_repos

runner = CliRunner()

FEATURE_ARGS = [
    "--name",
    "Auth Service",
    "--user-value",
    "8",
    "--time-crit",
    "5",
    "--risk-reduction",
    "3",
    "--job-size",
    "4",
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
    test_console = Console(file=buf, highlight=False, markup=False, width=200)
    monkeypatch.setattr(story_module, "console", test_console)
    yield buf


def invoke(db_path: Path, *args):
    return runner.invoke(app, ["--db-path", str(db_path)] + list(args))


def repos_for(db_path: Path):
    return get_repos(get_db(db_path))


def _setup(db_path):
    invoke(db_path, "feature", "add", *FEATURE_ARGS)
    invoke(db_path, "team", "create", "--name", "Alpha", "--members", "6")
    repos = repos_for(db_path)
    feature = repos.features.get_all()[0]
    team = repos.teams.get_all()[0]
    return feature.id, team.id


def _add_story(db_path, feature_id, team_id, name="Login flow", points="3"):
    return invoke(
        db_path,
        "story",
        "add",
        "--name",
        name,
        "--feature-id",
        feature_id,
        "--team-id",
        team_id,
        "--points",
        points,
    )


class TestStoryAdd:
    def test_exit_code_success(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        result = _add_story(db_path, fid, tid)
        assert result.exit_code == 0

    def test_stored_in_db(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        stories = repos_for(db_path).stories.get_all()
        assert len(stories) == 1
        assert stories[0].name == "Login flow"
        assert stories[0].points == 3

    def test_added_to_feature_story_ids(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        feature = repos_for(db_path).features.get(fid)
        assert story.id in feature.story_ids

    def test_unknown_feature_exits_1(self, db_path, patch_console):
        _, tid = _setup(db_path)
        result = invoke(
            db_path,
            "story",
            "add",
            "--name",
            "S",
            "--feature-id",
            "bad",
            "--team-id",
            tid,
            "--points",
            "3",
        )
        assert result.exit_code == 1

    def test_unknown_team_exits_1(self, db_path, patch_console):
        fid, _ = _setup(db_path)
        result = invoke(
            db_path,
            "story",
            "add",
            "--name",
            "S",
            "--feature-id",
            fid,
            "--team-id",
            "bad",
            "--points",
            "3",
        )
        assert result.exit_code == 1

    def test_zero_points_exits_1(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        result = _add_story(db_path, fid, tid, points="0")
        assert result.exit_code == 1


class TestStoryList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "story", "list")
        assert "No stories found" in patch_console.getvalue()

    def test_lists_story(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "story", "list")
        assert "Login flow" in patch_console.getvalue()

    def test_filter_by_feature(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        invoke(db_path, "feature", "add", *FEATURE_ARGS)
        fid2 = repos_for(db_path).features.get_all()[1].id
        _add_story(db_path, fid, tid, name="S1")
        _add_story(db_path, fid2, tid, name="S2")
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "story", "list", "--feature-id", fid)
        output = patch_console.getvalue()
        assert "S1" in output
        assert "S2" not in output


class TestStoryUpdate:
    def test_update_status(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        invoke(db_path, "story", "update", story.id, "--status", "in_progress")
        updated = repos_for(db_path).stories.get(story.id)
        assert updated.status.value == "in_progress"

    def test_update_points(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        invoke(db_path, "story", "update", story.id, "--points", "8")
        updated = repos_for(db_path).stories.get(story.id)
        assert updated.points == 8

    def test_invalid_status_exits_1(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        result = invoke(db_path, "story", "update", story.id, "--status", "bad")
        assert result.exit_code == 1

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "story", "update", "no-such-id", "--name", "X")
        assert result.exit_code == 1


class TestStoryDelete:
    def test_removes_story(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        invoke(db_path, "story", "delete", story.id)
        assert repos_for(db_path).stories.get(story.id) is None

    def test_removes_from_feature_story_ids(self, db_path, patch_console):
        fid, tid = _setup(db_path)
        _add_story(db_path, fid, tid)
        story = repos_for(db_path).stories.get_all()[0]
        invoke(db_path, "story", "delete", story.id)
        feature = repos_for(db_path).features.get(fid)
        assert story.id not in feature.story_ids

    def test_unknown_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "story", "delete", "no-such-id")
        assert result.exit_code == 1

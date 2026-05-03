from io import StringIO
from pathlib import Path

import pytest
from rich.console import Console
from typer.testing import CliRunner

import safe.cli.art as art_module
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
    test_console = Console(file=buf, highlight=False, markup=False)
    monkeypatch.setattr(art_module, "console", test_console)
    yield buf


def invoke(db_path: Path, *args):
    return runner.invoke(app, ["--db-path", str(db_path)] + list(args))


def repos_for(db_path: Path):
    return get_repos(get_db(db_path))


# ---------------------------------------------------------------------------
# art create
# ---------------------------------------------------------------------------

class TestArtCreate:
    def test_exit_code_success(self, db_path, patch_console):
        result = invoke(db_path, "art", "create", "--name", "Platform ART")
        assert result.exit_code == 0

    def test_name_in_output(self, db_path, patch_console):
        invoke(db_path, "art", "create", "--name", "Platform ART")
        assert "Platform ART" in patch_console.getvalue()

    def test_id_in_output(self, db_path, patch_console):
        invoke(db_path, "art", "create", "--name", "Platform ART")
        assert "id:" in patch_console.getvalue()

    def test_stored_in_db(self, db_path, patch_console):
        invoke(db_path, "art", "create", "--name", "Platform ART")
        arts = repos_for(db_path).arts.get_all()
        assert len(arts) == 1
        assert arts[0].name == "Platform ART"

    def test_missing_name_exits_nonzero(self, db_path, patch_console):
        result = invoke(db_path, "art", "create")
        assert result.exit_code != 0

    def test_short_flag(self, db_path, patch_console):
        result = invoke(db_path, "art", "create", "-n", "Platform ART")
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# art show
# ---------------------------------------------------------------------------

class TestArtShow:
    def _create_art(self, db_path):
        invoke(db_path, "art", "create", "--name", "Platform ART")
        return repos_for(db_path).arts.get_all()[0]

    def test_shows_name(self, db_path, patch_console):
        art = self._create_art(db_path)
        invoke(db_path, "art", "show", art.id)
        assert "Platform ART" in patch_console.getvalue()

    def test_shows_id(self, db_path, patch_console):
        art = self._create_art(db_path)
        invoke(db_path, "art", "show", art.id)
        assert art.id in patch_console.getvalue()

    def test_exit_code_success(self, db_path, patch_console):
        art = self._create_art(db_path)
        result = invoke(db_path, "art", "show", art.id)
        assert result.exit_code == 0

    def test_missing_id_exits_1(self, db_path, patch_console):
        result = invoke(db_path, "art", "show", "nonexistent")
        assert result.exit_code == 1

    def test_missing_error_message(self, db_path, patch_console):
        invoke(db_path, "art", "show", "nonexistent")
        assert "Error" in patch_console.getvalue()


# ---------------------------------------------------------------------------
# art list
# ---------------------------------------------------------------------------

class TestArtList:
    def test_empty(self, db_path, patch_console):
        invoke(db_path, "art", "list")
        assert "No ARTs found" in patch_console.getvalue()

    def test_lists_all(self, db_path, patch_console):
        invoke(db_path, "art", "create", "--name", "Platform ART")
        invoke(db_path, "art", "create", "--name", "Business ART")
        patch_console.truncate(0)
        patch_console.seek(0)
        invoke(db_path, "art", "list")
        output = patch_console.getvalue()
        assert "Platform ART" in output
        assert "Business ART" in output

    def test_exit_code_success(self, db_path, patch_console):
        result = invoke(db_path, "art", "list")
        assert result.exit_code == 0

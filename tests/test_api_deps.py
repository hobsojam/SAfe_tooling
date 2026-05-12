import os
from unittest.mock import MagicMock

import pytest

import safe.api.deps as deps_module
from safe.api.deps import (
    _dev_session_file,
    _is_hot_reload,
    _write_dev_session,
    clear_cache,
    get_repos_dep,
)


class TestDevSessionFile:
    def test_returns_sibling_named_dev_session(self, tmp_path):
        db_path = tmp_path / "db.json"
        result = _dev_session_file(db_path)
        assert result == tmp_path / ".dev_session"


class TestIsHotReload:
    def test_false_when_no_session_file(self, tmp_path):
        db_path = tmp_path / "db.json"
        assert _is_hot_reload(db_path) is False

    def test_false_when_pid_differs(self, tmp_path):
        db_path = tmp_path / "db.json"
        _dev_session_file(db_path).write_text("1")  # PID 1 (init) is never our parent
        assert _is_hot_reload(db_path) is False

    def test_true_when_pid_matches_getppid(self, tmp_path):
        db_path = tmp_path / "db.json"
        _dev_session_file(db_path).write_text(str(os.getppid()))
        assert _is_hot_reload(db_path) is True


class TestWriteDevSession:
    def test_writes_parent_pid_as_string(self, tmp_path):
        db_path = tmp_path / "db.json"
        _write_dev_session(db_path)
        content = _dev_session_file(db_path).read_text().strip()
        assert content == str(os.getppid())


class TestGetReposDep:
    def test_raises_runtime_error_when_db_none(self, monkeypatch):
        monkeypatch.setattr(deps_module, "_db", None)
        gen = get_repos_dep()
        with pytest.raises(RuntimeError, match="Database not initialised"):
            next(gen)


class TestClearCache:
    def test_no_op_when_db_is_none(self, monkeypatch):
        monkeypatch.setattr(deps_module, "_db", None)
        clear_cache()  # must not raise

    def test_clears_all_table_caches(self, monkeypatch):
        mock_table = MagicMock()
        mock_db = MagicMock()
        mock_db.tables.return_value = ["_default", "features"]
        mock_db.table.return_value = mock_table
        monkeypatch.setattr(deps_module, "_db", mock_db)

        clear_cache()

        assert mock_db.table.call_count == 2
        assert mock_table.clear_cache.call_count == 2

import pytest
from fastapi.testclient import TestClient
from tinydb import TinyDB

from safe.api.deps import get_repos_dep
from safe.api.main import app
from safe.store.repos import Repos


@pytest.fixture
def db(tmp_path):
    database = TinyDB(tmp_path / "api_test.json")
    yield database
    database.close()


@pytest.fixture
def client(db):
    app.dependency_overrides[get_repos_dep] = lambda: Repos(db)
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

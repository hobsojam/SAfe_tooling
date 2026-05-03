def _setup(client):
    art_id = client.post("/art", json={"name": "ART"}).json()["id"]
    pi_id = client.post("/pi", json={
        "name": "PI 1", "art_id": art_id, "start_date": "2026-01-05", "end_date": "2026-03-27",
    }).json()["id"]
    team_id = client.post("/team", json={"name": "Alpha", "member_count": 7}).json()["id"]
    iter_id = client.post("/iterations", json={
        "pi_id": pi_id, "number": 1, "start_date": "2026-01-05", "end_date": "2026-01-16",
    }).json()["id"]
    return pi_id, team_id, iter_id


def _create_plan(client, pi_id, team_id, iter_id, **overrides):
    return client.post("/capacity-plans", json={
        "pi_id": pi_id, "team_id": team_id, "iteration_id": iter_id,
        "team_size": 7, **overrides,
    })


def test_create_returns_201(client):
    pi_id, team_id, iter_id = _setup(client)
    r = _create_plan(client, pi_id, team_id, iter_id)
    assert r.status_code == 201
    body = r.json()
    assert "available_capacity" in body
    assert body["available_capacity"] > 0


def test_create_upserts_existing(client):
    pi_id, team_id, iter_id = _setup(client)
    plan_id = _create_plan(client, pi_id, team_id, iter_id).json()["id"]
    r = _create_plan(client, pi_id, team_id, iter_id, team_size=5)
    assert r.status_code == 201
    assert r.json()["id"] == plan_id
    assert r.json()["team_size"] == 5


def test_list_filter_by_pi(client):
    pi_id, team_id, iter_id = _setup(client)
    _create_plan(client, pi_id, team_id, iter_id)
    plans = client.get(f"/capacity-plans?pi_id={pi_id}").json()
    assert len(plans) == 1


def test_get_returns_plan(client):
    pi_id, team_id, iter_id = _setup(client)
    plan_id = _create_plan(client, pi_id, team_id, iter_id).json()["id"]
    r = client.get(f"/capacity-plans/{plan_id}")
    assert r.status_code == 200
    assert r.json()["id"] == plan_id


def test_get_unknown_returns_404(client):
    assert client.get("/capacity-plans/no-such-id").status_code == 404


def test_patch_team_size(client):
    pi_id, team_id, iter_id = _setup(client)
    plan_id = _create_plan(client, pi_id, team_id, iter_id).json()["id"]
    r = client.patch(f"/capacity-plans/{plan_id}", json={"team_size": 10})
    assert r.status_code == 200
    assert r.json()["team_size"] == 10


def test_delete_returns_204(client):
    pi_id, team_id, iter_id = _setup(client)
    plan_id = _create_plan(client, pi_id, team_id, iter_id).json()["id"]
    assert client.delete(f"/capacity-plans/{plan_id}").status_code == 204
    assert client.get(f"/capacity-plans/{plan_id}").status_code == 404

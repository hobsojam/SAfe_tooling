def _create_art(client):
    return client.post("/art", json={"name": "ART"}).json()["id"]


def _create_pi(client, art_id):
    return client.post("/pi", json={"name": "PI 1", "art_id": art_id, "start_date": "2026-01-05", "end_date": "2026-03-27"}).json()["id"]


def _create_teams(client):
    t1 = client.post("/team", json={"name": "Alpha", "member_count": 5}).json()["id"]
    t2 = client.post("/team", json={"name": "Beta", "member_count": 5}).json()["id"]
    return t1, t2


def _create_dep(client, pi_id, t1, t2, **overrides):
    return client.post("/dependencies", json={
        "description": "Needs auth API", "pi_id": pi_id,
        "from_team_id": t1, "to_team_id": t2, **overrides,
    })


def test_create_returns_201(client):
    art_id = _create_art(client)
    pi_id = _create_pi(client, art_id)
    t1, t2 = _create_teams(client)
    r = _create_dep(client, pi_id, t1, t2)
    assert r.status_code == 201
    assert r.json()["status"] == "identified"


def test_list_filter_by_pi(client):
    art_id = _create_art(client)
    pi1 = _create_pi(client, art_id)
    pi2 = client.post("/pi", json={"name": "PI 2", "art_id": art_id, "start_date": "2026-04-06", "end_date": "2026-06-26"}).json()["id"]
    t1, t2 = _create_teams(client)
    _create_dep(client, pi1, t1, t2)
    _create_dep(client, pi2, t1, t2)
    deps = client.get(f"/dependencies?pi_id={pi1}").json()
    assert len(deps) == 1


def test_roam_sets_status(client):
    art_id = _create_art(client)
    pi_id = _create_pi(client, art_id)
    t1, t2 = _create_teams(client)
    did = _create_dep(client, pi_id, t1, t2).json()["id"]
    r = client.post(f"/dependencies/{did}/roam", json={"status": "resolved", "resolution_notes": "Done"})
    assert r.status_code == 200
    assert r.json()["status"] == "resolved"


def test_roam_unknown_returns_404(client):
    assert client.post("/dependencies/no-such-id/roam", json={"status": "resolved"}).status_code == 404


def test_get_unknown_returns_404(client):
    assert client.get("/dependencies/no-such-id").status_code == 404


def test_delete_returns_204(client):
    art_id = _create_art(client)
    pi_id = _create_pi(client, art_id)
    t1, t2 = _create_teams(client)
    did = _create_dep(client, pi_id, t1, t2).json()["id"]
    assert client.delete(f"/dependencies/{did}").status_code == 204
    assert client.get(f"/dependencies/{did}").status_code == 404

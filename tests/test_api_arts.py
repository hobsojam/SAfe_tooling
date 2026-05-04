def test_list_empty(client):
    r = client.get("/art")
    assert r.status_code == 200
    assert r.json() == []


def test_create_returns_201(client):
    r = client.post("/art", json={"name": "Platform ART"})
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Platform ART"
    assert "id" in body
    assert body["team_ids"] == []


def test_create_missing_name_returns_422(client):
    r = client.post("/art", json={})
    assert r.status_code == 422


def test_get_returns_art(client):
    art_id = client.post("/art", json={"name": "My ART"}).json()["id"]
    r = client.get(f"/art/{art_id}")
    assert r.status_code == 200
    assert r.json()["id"] == art_id


def test_get_unknown_returns_404(client):
    r = client.get("/art/no-such-id")
    assert r.status_code == 404


def test_patch_name(client):
    art_id = client.post("/art", json={"name": "Old Name"}).json()["id"]
    r = client.patch(f"/art/{art_id}", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


def test_patch_unknown_returns_404(client):
    r = client.patch("/art/no-such-id", json={"name": "X"})
    assert r.status_code == 404


def test_patch_empty_body_is_noop(client):
    art_id = client.post("/art", json={"name": "Stable"}).json()["id"]
    r = client.patch(f"/art/{art_id}", json={})
    assert r.status_code == 200
    assert r.json()["name"] == "Stable"


def test_delete_returns_204(client):
    art_id = client.post("/art", json={"name": "Temp"}).json()["id"]
    r = client.delete(f"/art/{art_id}")
    assert r.status_code == 204
    assert client.get(f"/art/{art_id}").status_code == 404


def test_delete_with_team_returns_409(client):
    art_id = client.post("/art", json={"name": "ART"}).json()["id"]
    client.post("/team", json={"name": "Alpha", "member_count": 6, "art_id": art_id})
    assert client.delete(f"/art/{art_id}").status_code == 409


def test_delete_with_pi_returns_409(client):
    art_id = client.post("/art", json={"name": "ART"}).json()["id"]
    client.post(
        "/pi",
        json={
            "name": "PI 1",
            "art_id": art_id,
            "start_date": "2026-01-05",
            "end_date": "2026-03-27",
        },
    )
    assert client.delete(f"/art/{art_id}").status_code == 409


def test_delete_unknown_returns_404(client):
    r = client.delete("/art/no-such-id")
    assert r.status_code == 404


def test_list_returns_all(client):
    client.post("/art", json={"name": "ART 1"})
    client.post("/art", json={"name": "ART 2"})
    arts = client.get("/art").json()
    assert len(arts) == 2

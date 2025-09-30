def test_solutions_index(app_client):
    resp = app_client.get("/api/solutions/index")
    assert resp.status_code == 200
    body = resp.json()
    assert "datasets" in body
    names = [d["name"] for d in body["datasets"]]
    assert "python" in names


def test_solution_dataset_success(app_client):
    resp = app_client.get("/api/solutions?name=python")
    assert resp.status_code == 200
    data = resp.json()
    # In isolated fixture mode we expect 1; with real dataset present we just assert non-empty.
    assert len(data) >= 1
    # Basic shape expectations
    first = data[0]
    assert "vulnerability_id" in first
    assert "title" in first


def test_solution_dataset_missing(app_client):
    resp = app_client.get("/api/solutions?name=not-there")
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert detail["error"] == "solutions dataset not found"

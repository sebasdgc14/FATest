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
    assert len(data) == 1
    assert data[0]["vulnerability_id"] == "VULN-1"


def test_solution_dataset_missing(app_client):
    resp = app_client.get("/api/solutions?name=not-there")
    assert resp.status_code == 404
    detail = resp.json()["detail"]
    assert detail["error"] == "solutions dataset not found"

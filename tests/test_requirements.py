def test_requirements_both(app_client):
    resp = app_client.get("/api/requirements?lang=both")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    item = data[0]
    assert "en" in item and "es" in item


def test_requirements_single_lang_en(app_client):
    resp = app_client.get("/api/requirements?lang=en")
    assert resp.status_code == 200
    item = resp.json()[0]
    assert "en" in item
    assert item["es"] is None


def test_requirements_single_lang_es(app_client):
    resp = app_client.get("/api/requirements?lang=es")
    assert resp.status_code == 200
    item = resp.json()[0]
    assert "es" in item
    assert item["en"] is None

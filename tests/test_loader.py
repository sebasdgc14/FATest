from backend.loader import load_json


def test_load_json_not_found(tmp_path):
    data, err = load_json(tmp_path / "missing.json")
    assert data is None
    assert err and err.kind == "not_found"


def test_load_json_invalid_json(tmp_path):
    f = tmp_path / "bad.json"
    f.write_text("{\n  invalid\n}")
    data, err = load_json(f)
    assert data is None
    assert err and err.kind == "invalid_json"


def test_load_json_valid(tmp_path):
    f = tmp_path / "ok.json"
    f.write_text('[{"a": 1}]')
    data, err = load_json(f)
    assert err is None
    assert isinstance(data, list)

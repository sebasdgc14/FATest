import json
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.main import create_app


# ---------------------------------------------------------------------------
# Helper builders (pure) to create dataset structures for tests
# ---------------------------------------------------------------------------
def build_requirement(
    _id: str = "REQ-1",
    category: str = "general",
    title_en: str = "Title EN",
    title_es: str = "Titulo ES",
) -> dict:
    return {
        "id": _id,
        "category": category,
        "en": {"title": title_en, "summary": "S", "description": "D"},
        "es": {"title": title_es, "summary": "R", "description": "Desc"},
        "references": ["RFC-1"],
        "supported_in": {"python": True},
        "metadata": {"level": "base"},
        "last_update_time": None,
    }


def build_compliance(
    _id: str = "C-1",
    title: str = "Control 1",
) -> dict:
    return {
        "id": _id,
        "title": title,
        "en": {"summary": "English summary"},
        "es": {"summary": "Resumen"},
        "definitions": [],
        "metadata": {},
        "last_update_time": None,
    }


def build_vulnerability(
    _id: str = "V-1",
    category: str = "cat",
) -> dict:
    return {
        "id": _id,
        "category": category,
        "en": {
            "title": "Vuln EN",
            "description": "Desc EN",
            "impact": "Impact EN",
            "recommendation": "Rec EN",
            "threat": "Threat EN",
        },
        "es": {
            "title": "Vuln ES",
            "description": "Desc ES",
            "impact": "Impact ES",
            "recommendation": "Rec ES",
            "threat": "Threat ES",
        },
        "examples": None,
        "remediation_time": None,
        "score": None,
        "score_v4": None,
        "requirements": [],
        "metadata": {},
        "last_update_time": None,
    }


def build_solution_dataset() -> list[dict]:
    return [
        {
            "vulnerability_id": "VULN-1",
            "title": "Python Issue",
            "context": ["context line"],
            "need": "Fix something",
            "solution": {
                "language": "python",
                "steps": ["one", "two"],
                "insecure_code_example": {"text": "bad()"},
                "secure_code_example": {"text": "good()"},
            },
        }
    ]


# ---------------------------------------------------------------------------
# Core data_root fixture writing JSON files for the app factory
# ---------------------------------------------------------------------------
@pytest.fixture()
def data_root(tmp_path: Path) -> Path:
    (tmp_path / "requirements.json").write_text(json.dumps([build_requirement()]))
    (tmp_path / "compliance.json").write_text(json.dumps([build_compliance()]))
    (tmp_path / "vulnerabilities.json").write_text(json.dumps([build_vulnerability()]))

    solutions_dir = tmp_path / "solutions_json"
    solutions_dir.mkdir()
    (solutions_dir / "python.json").write_text(json.dumps(build_solution_dataset()))
    return tmp_path


# ---------------------------------------------------------------------------
# Additional fixtures for direct dataset inspection in tests (optional usage)
# ---------------------------------------------------------------------------
@pytest.fixture()
def requirement_sample() -> dict:
    return build_requirement()


@pytest.fixture()
def vulnerability_sample() -> dict:
    return build_vulnerability()


@pytest.fixture()
def compliance_sample() -> dict:
    return build_compliance()


# ---------------------------------------------------------------------------
# FastAPI TestClient fixture
# ---------------------------------------------------------------------------
@pytest.fixture()
def app_client(data_root: Path):
    app = create_app(data_root=data_root)
    with TestClient(app) as client:
        yield client

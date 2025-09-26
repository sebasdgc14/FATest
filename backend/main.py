from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import json
from typing import List, Literal
from backend.models import (
    RequirementOut,
    ComplianceOut,
    VulnerabilityOut,
    SolutionOut,
)

app = FastAPI(title="PyYAML API")

# Allow React dev server to call this API (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite default dev origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


DATA_ROOT = Path(__file__).resolve().parents[1]


def _read_json(filename: str):
    path = DATA_ROOT / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"{filename} not found")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Invalid JSON in {filename}: {e}")


def _filter_lang(items: List[dict], lang: str) -> List[dict]:
    if lang not in {"en", "es", "both"}:
        return items
    if lang == "both":
        return items
    filtered = []
    for it in items:
        it_copy = dict(it)
        # Remove the other language block if present
        other = "es" if lang == "en" else "en"
        if other in it_copy:
            it_copy.pop(other, None)
        filtered.append(it_copy)
    return filtered


@app.get("/api/requirements", response_model=List[RequirementOut])
def api_requirements(
    lang: Literal["en", "es", "both"] = Query(
        "both", description="Return only one language block or both"
    ),
):
    data = _read_json("requirements.json")
    if not isinstance(data, list):
        raise HTTPException(
            status_code=500, detail="requirements.json root must be a list"
        )
    return _filter_lang(data, lang)


@app.get("/api/compliance", response_model=List[ComplianceOut])
def api_compliance(
    lang: Literal["en", "es", "both"] = Query(
        "both", description="Return only one language block or both"
    ),
):
    data = _read_json("compliance.json")
    if not isinstance(data, list):
        raise HTTPException(
            status_code=500, detail="compliance.json root must be a list"
        )
    return _filter_lang(data, lang)


@app.get("/api/vulnerabilities", response_model=List[VulnerabilityOut])
def api_vulnerabilities(
    lang: Literal["en", "es", "both"] = Query(
        "both", description="Return only one language block or both"
    ),
):
    data = _read_json("vulnerabilities.json")
    if not isinstance(data, list):
        raise HTTPException(
            status_code=500, detail="vulnerabilities.json root must be a list"
        )
    return _filter_lang(data, lang)


# WATCH OUT HERE, ONLY ANDROID IS RECOGNIZED WE NEED TO ADD THE REST!!!
@app.get("/api/solutions", response_model=List[SolutionOut])
def api_solutions():
    data = _read_json("solutions_android.json")
    if not isinstance(data, list):
        raise HTTPException(
            status_code=500, detail="solutions.json root must be a list"
        )
    return data


@app.get("/api/hub")
def api_hub():
    datasets = []
    for name in ["requirements", "compliance", "vulnerabilities", "solutions"]:
        filename = f"{name}.json"
        path = DATA_ROOT / filename
        exists = path.exists()
        count = 0
        if exists:
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    count = len(data)
            except Exception:
                pass
        datasets.append(
            {
                "name": name,
                "endpoint": f"/api/{name}",
                "file": filename,
                "exists": exists,
                "count": count,
            }
        )
    return {"datasets": datasets}

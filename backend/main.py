from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from backend.loader import load_json
from backend.models import (
    ComplianceOut,
    RequirementOut,
    SolutionOut,
    SolutionsIndexItem,
    SolutionsIndexOut,
    VulnerabilityOut,
)


def _filter_lang(items: list[dict], lang: str) -> list[dict]:
    if lang not in {"en", "es", "both"}:
        return items
    if lang == "both":
        return items
    other = "es" if lang == "en" else "en"
    return [{k: v for k, v in it.items() if k != other} for it in items]


def create_app(data_root: Path | None = None) -> FastAPI:
    """Application factory for improved testability & functional style."""
    data_root = data_root or Path(__file__).resolve().parents[1]
    solutions_dir = data_root / "solutions_json"

    app = FastAPI(title="PyYAML API")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():  # pragma: no cover - trivial
        return {"status": "ok"}

    def _load_list(filename: str) -> list[dict]:
        path = data_root / filename
        data, err = load_json(path)
        if err:
            if err.kind == "not_found":
                raise HTTPException(status_code=404, detail=err.detail)
            raise HTTPException(status_code=500, detail=err.detail)
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail=f"{filename} root must be a list")
        return data

    @app.get("/api/requirements", response_model=list[RequirementOut])
    def api_requirements(
        lang: Literal["en", "es", "both"] = Query(
            "both", description="Return only one language block or both"
        ),
    ):
        return _filter_lang(_load_list("requirements.json"), lang)

    @app.get("/api/compliance", response_model=list[ComplianceOut])
    def api_compliance(
        lang: Literal["en", "es", "both"] = Query(
            "both", description="Return only one language block or both"
        ),
    ):
        return _filter_lang(_load_list("compliance.json"), lang)

    @app.get("/api/vulnerabilities", response_model=list[VulnerabilityOut])
    def api_vulnerabilities(
        lang: Literal["en", "es", "both"] = Query(
            "both", description="Return only one language block or both"
        ),
    ):
        return _filter_lang(_load_list("vulnerabilities.json"), lang)

    @app.get("/api/solutions", response_model=list[SolutionOut])
    def api_solutions(
        name: str = Query(
            ...,  # required
            description=(
                "Solutions dataset name (filename stem) such as 'android' or 'aws'. "
                "Must match a JSON file named <name>.json inside solutions_json/."
            ),
        ),
    ):
        if not solutions_dir.exists():
            raise HTTPException(status_code=404, detail="solutions directory missing")
        fname = f"{name}.json" if not name.endswith(".json") else name
        path = solutions_dir / fname
        data, err = load_json(path)
        if err:
            if err.kind == "not_found":
                available = sorted(p.name for p in solutions_dir.glob("*.json"))
                raise HTTPException(
                    status_code=404,
                    detail={
                        "error": "solutions dataset not found",
                        "requested": fname,
                        "available": available,
                    },
                )
            raise HTTPException(status_code=500, detail=err.detail)
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail=f"{path.name} root must be a list")
        return data

    @app.get("/api/solutions/index", response_model=SolutionsIndexOut)
    def api_solutions_index():
        if not solutions_dir.exists():
            return {"datasets": []}
        items: list[SolutionsIndexItem] = []
        for p in sorted(solutions_dir.glob("*.json")):
            data, err = load_json(p)
            if err:
                items.append(
                    SolutionsIndexItem(
                        name=p.stem,
                        error="invalid_json" if err.kind == "invalid_json" else err.kind,
                    )
                )
                continue
            if isinstance(data, list):
                items.append(SolutionsIndexItem(name=p.stem, count=len(data)))
            else:
                items.append(SolutionsIndexItem(name=p.stem, error="root_not_list"))
        return {"datasets": items}

    @app.get("/api/hub")
    def api_hub():
        datasets = []
        for core in ["requirements", "compliance", "vulnerabilities"]:
            filename = f"{core}.json"
            path = data_root / filename
            exists = path.exists()
            datasets.append(
                {
                    "name": core,
                    "endpoint": f"/api/{core}",
                    "file": filename,
                    "exists": exists,
                }
            )
        solutions_summary = {
            "name": "solutions",
            "endpoint": "/api/solutions?name=<dataset>",
            "directory": str(solutions_dir.relative_to(data_root))
            if solutions_dir.exists()
            else None,
            "exists": solutions_dir.exists(),
            "sources": [],
        }
        if solutions_dir.exists():
            for p in sorted(solutions_dir.glob("*.json")):
                data, err = load_json(p)
                if err or not isinstance(data, list):
                    solutions_summary["sources"].append(
                        {
                            "name": p.stem,
                            "error": err.kind if err else "root_not_list",
                        }
                    )
                else:
                    solutions_summary["sources"].append({"name": p.stem})
        datasets.append(solutions_summary)
        return {"datasets": datasets}

    return app


app = create_app()

import os
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import TypeAdapter, ValidationError

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
    """Application factory.

    Data directory resolution order (unless explicitly provided):
      1. Env var APP_CORE_DATA_DIR (core JSON: requirements.json, etc.)
      2. <repo_root>/data/core
      3. <repo_root>/data/solutions (fallback if core misplaced there)
      4. <repo_root> (legacy layout)

    Solutions directory resolution order:
      1. Env var APP_SOLUTIONS_DIR
      2. <repo_root>/data/solutions/solutions_json
      3. <repo_root>/data/solutions
      4. <core_data_dir>/solutions_json (legacy within core root)
      5. <repo_root>/solutions_json (legacy root)
    """
    repo_root = Path(__file__).resolve().parents[1]

    # Core data root
    if data_root is not None:
        core_dir = data_root
    else:
        env_core = os.getenv("APP_CORE_DATA_DIR")
        if env_core:
            core_dir = Path(env_core)
        else:
            candidates = [
                repo_root / "data" / "core",
                repo_root / "data" / "solutions",  # fallback if user placed core files here
                repo_root,  # legacy
            ]
            core_dir = next((c for c in candidates if c.exists()), candidates[-1])

    # Solutions directory
    env_solutions = os.getenv("APP_SOLUTIONS_DIR")
    if env_solutions:
        solutions_dir = Path(env_solutions)
    else:
        sol_candidates = [
            repo_root / "data" / "solutions" / "solutions_json",
            repo_root / "data" / "solutions",
            core_dir / "solutions_json",
            repo_root / "solutions_json",
        ]
        solutions_dir = next((c for c in sol_candidates if c.exists()), sol_candidates[-1])

    app = FastAPI(title="PyYAML API")

    # ------------------------------------------------------------------
    # Eager validation setup
    # ------------------------------------------------------------------
    # We validate core JSON datasets at startup so that structural issues
    # fail fast instead of surfacing only on first request. Results are
    # cached (as plain dicts) to avoid re-validating on every request.
    # Can be disabled by setting APP_DISABLE_EAGER_VALIDATION=1.
    disable_eager = os.getenv("APP_DISABLE_EAGER_VALIDATION") == "1"
    validated_cache: dict[str, list[dict[str, Any]]] = {}

    core_adapters: dict[str, TypeAdapter] = {
        "requirements.json": TypeAdapter(list[RequirementOut]),
        "compliance.json": TypeAdapter(list[ComplianceOut]),
        "vulnerabilities.json": TypeAdapter(list[VulnerabilityOut]),
    }

    if not disable_eager:
        for fname, adapter in core_adapters.items():
            path = core_dir / fname
            if not path.exists():
                continue  # absence is not fatal; endpoint will 404 later
            data, err = load_json(path)
            if err:
                # Treat invalid JSON or other IO issues as startup failure.
                raise RuntimeError(f"Failed loading {fname}: {err.detail}")
            if not isinstance(data, list):
                raise RuntimeError(f"{fname} root must be a list")
            try:
                validated = adapter.validate_python(data)
            except ValidationError as e:
                raise RuntimeError(f"Validation error in {fname}: {len(e.errors())} issues") from e
            # Store as list[dict] to keep response_model flow unchanged and
            # allow subsequent filtering logic to operate on dicts.
            validated_cache[fname] = [m.model_dump() for m in validated]

    # Adapter for solutions datasets (validated lazily & cached per file)
    solutions_adapter = TypeAdapter(list[SolutionOut])
    solutions_validated_cache: dict[str, list[dict[str, Any]]] = {}
    # -----------------------
    # CORS configuration
    # -----------------------
    origins_env = os.getenv("APP_ALLOW_ORIGINS")
    if origins_env:
        if origins_env.strip() == "*":
            allow_origins = ["*"]
        else:
            allow_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
    else:
        allow_origins = ["http://localhost:5173"]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health")
    def health():  # pragma: no cover - trivial
        return {"status": "ok"}

    def _load_list(filename: str) -> list[dict]:
        # If we have a validated cache entry, return a shallow copy to avoid accidental mutation
        if filename in validated_cache:
            return [dict(item) for item in validated_cache[filename]]

        # Fallback path-based loading (legacy or when eager validation disabled)
        primary = core_dir / filename
        path = primary if primary.exists() else repo_root / filename
        data, err = load_json(path)
        if err:
            if err.kind == "not_found":
                raise HTTPException(status_code=404, detail=err.detail)
            raise HTTPException(status_code=500, detail=err.detail)
        if not isinstance(data, list):
            raise HTTPException(status_code=500, detail=f"{filename} root must be a list")

        # Validate on-demand if eager disabled
        adapter = core_adapters.get(filename)
        if adapter is not None and disable_eager:
            try:
                validated = adapter.validate_python(data)
            except ValidationError as e:
                raise HTTPException(
                    status_code=500,
                    detail={
                        "file": filename,
                        "errors": e.errors(),
                    },
                ) from e
            data = [m.model_dump() for m in validated]
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

        # Lazy validation & caching for solutions datasets
        cache_key = path.name
        if cache_key in solutions_validated_cache:
            return [dict(item) for item in solutions_validated_cache[cache_key]]
        try:
            validated = solutions_adapter.validate_python(data)
        except ValidationError as e:
            raise HTTPException(
                status_code=500,
                detail={
                    "file": path.name,
                    "errors": e.errors(),
                },
            ) from e
        dumped = [m.model_dump() for m in validated]
        solutions_validated_cache[cache_key] = dumped
        return dumped

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
            path = core_dir / filename
            exists = path.exists()
            datasets.append(
                {
                    "name": core,
                    "endpoint": f"/api/{core}",
                    "file": filename,
                    "exists": exists,
                }
            )
        if solutions_dir.exists():
            try:
                rel_dir = str(solutions_dir.relative_to(core_dir))
            except ValueError:
                # Fallback if solutions_dir is outside core_dir hierarchy
                rel_dir = str(solutions_dir)
        else:
            rel_dir = None
        solutions_summary = {
            "name": "solutions",
            "endpoint": "/api/solutions?name=<dataset>",
            "directory": rel_dir,
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

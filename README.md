# FATest (FastAPI + React/Vite Test & Data Workspace)

A small full‑stack workspace combining:

- **Backend**: FastAPI service exposing requirements, compliance, vulnerabilities, and solutions datasets.
- **Frontend**: React + Vite + TypeScript interface to explore and filter the data.
- **Data Pipelines**: Normalization & build scripts to transform raw YAML into curated JSON served by the API.
- **Testing**: Pytest (backend) + Vitest / Testing Library (frontend).
- **Tooling**: Ruff (lint + format) for Python and Prettier + ESLint for the frontend.

---

## Contents

- [Folder Structure](#folder-structure)
- [Data Layout & Environment Overrides](#data-layout--environment-overrides)
- [Scripts](#scripts)
- [Backend (FastAPI)](#backend-fastapi)
- [Frontend (Vite/React)](#frontend-vitereact)
- [Testing](#testing)
- [Development Workflow](#development-workflow)
- [Formatting & Linting](#formatting--linting)
- [Conventional Commits](#conventional-commits)
- [Extending / Next Ideas](#extending--next-ideas)

---

## Folder Structure

```
.
├── backend/
│   ├── main.py              # FastAPI app factory + routes
│   ├── loader.py            # Pure JSON loader helper
│   ├── models.py            # Pydantic response models
├── data/
│   ├── core/                # (Target location for canonical JSON: requirements.json, etc.)
│   ├── solutions/           # Solutions datasets (may contain solutions_json/)
│   │   └── solutions_json/  # Generated per-language/platform solution JSON files
│   └── raw/                 # Source YAML inputs (requirements_data.yaml, etc.)
├── frontend/                # Vite + React + TypeScript app
│   ├── src/pages/           # Page components (Requirements, Compliance, etc.)
│   └── src/pages/__tests__/ # Vitest smoke tests
├── scripts/
│   ├── Normalizing.py       # Normalization utilities
│   ├── run_parse.py         # Builds core JSON from raw YAML
│   └── build_solutions.py   # Builds solutions JSON datasets
├── tests/                   # Pytest backend tests
├── pyproject.toml           # Ruff configuration
├── requirements.txt         # Python deps
└── README.md
```

---

## Data Layout & Environment Overrides

The backend auto‑detects data paths in a flexible order so you can reorganize without breaking things.

### Core JSON (requirements, compliance, vulnerabilities)

Resolution order (first existing wins):

1. `data_root` argument passed to `create_app()` (tests use this)
2. `APP_CORE_DATA_DIR` environment variable
3. `<repo>/data/core`
4. `<repo>/data/solutions` (fallback if misplaced)
5. `<repo>` (legacy root layout)

### Solutions JSON Directory

Resolution order:

1. `APP_SOLUTIONS_DIR`
2. `<repo>/data/solutions/solutions_json`
3. `<repo>/data/solutions`
4. `<core_dir>/solutions_json`
5. `<repo>/solutions_json` (legacy)

### Script Overrides

`run_parse.py` & `build_solutions.py` honor these env variables:

- `RAW_CORE_DIR` (default: `data/raw`)
- `CORE_OUTPUT_DIR` (default: `data/core`)
- `RAW_SOLUTIONS_DIR` (default: `data/raw/solutions_yaml`)
- `SOLUTIONS_OUTPUT_DIR` (default: `data/solutions/solutions_json`)

Example (PowerShell):

```
$env:RAW_CORE_DIR="C:/workspace/custom/raw"; $env:CORE_OUTPUT_DIR="C:/workspace/out/core"; python scripts/run_parse.py
```

---

## Scripts

| Script                       | Purpose                                                                                      | Typical Use                                  |
| ---------------------------- | -------------------------------------------------------------------------------------------- | -------------------------------------------- |
| `scripts/run_parse.py`       | Parse & normalize raw YAML (requirements/compliance/vulnerabilities) into `data/core/*.json` | Rebuild core datasets after editing raw YAML |
| `scripts/build_solutions.py` | Convert solution YAML files into individual solution JSON datasets                           | Update solutions after adding/modifying YAML |
| `scripts/Normalizing.py`     | Shared normalization & parsing helpers                                                       | Imported by the other scripts                |

---

## Backend (FastAPI)

Exports an application factory: `create_app(data_root: Path | None = None)`. A module-level `app = create_app()` is defined for ASGI servers.

### Run (development)

```
uvicorn backend.main:app --reload --port 8000
```

### Key Endpoints

| Path                            | Method | Description                                         |
| ------------------------------- | ------ | --------------------------------------------------- | --- | -------------------------------------- |
| `/health`                       | GET    | Liveness check                                      |
| `/api/requirements?lang=both    | en     | es`                                                 | GET | Requirements dataset (language filter) |
| `/api/compliance?lang=...`      | GET    | Compliance dataset                                  |
| `/api/vulnerabilities?lang=...` | GET    | Vulnerabilities dataset                             |
| `/api/solutions?name=python`    | GET    | Specific solutions dataset JSON                     |
| `/api/solutions/index`          | GET    | Listing & quick metadata for all solutions datasets |
| `/api/hub`                      | GET    | Summary of available core & solutions datasets      |

Language filtering prunes the opposite language field content (Pydantic returns the missing one as `null`).

---

## Frontend (Vite/React/TS)

- Entry: `frontend/src/main.tsx`
- Pages: `RequirementsPage`, `CompliancePage`, `VulnerabilitiesPage`, `SolutionsPage`
- Each page fetches from the local FastAPI backend (defaults to `http://localhost:8000`).

Dev server (from `frontend/`):

```
npm install
npm run dev
```

Run the backend in parallel (other terminal) for live data.

---

## Testing

### Backend (pytest)

From repo root:

```
pytest -q
```

Tests generate ephemeral JSON into a temp directory via fixtures—no dependency on real `data/` layout.

### Frontend (Vitest)

From `frontend/`:

```
npm run test:run
```

The current suite includes smoke tests for each main page with mocked `fetch`.

---

## Development Workflow

1. (Optional) Create venv & install Python deps:
   ```
   python -m venv .venv
   .\.venv\Scripts\activate
   pip install -r requirements.txt
   ```
2. Install frontend deps: `cd frontend && npm install`
3. (If raw YAML changed) run:
   ```
   python scripts/run_parse.py
   python scripts/build_solutions.py
   ```
4. Start backend: `uvicorn backend.main:app --reload`
5. Start frontend: `npm run dev`
6. Run tests (backend/frontend) before committing.

---

## Formatting & Linting

| Area            | Tool     | Commands                                  |
| --------------- | -------- | ----------------------------------------- |
| Python lint     | Ruff     | `ruff check .`                            |
| Python format   | Ruff     | `ruff format .`                           |
| Frontend lint   | ESLint   | `npm run lint` (from `frontend/`)         |
| Frontend format | Prettier | `npm run format` / `npm run format:check` |

Consider pre-commit hooks later (e.g., using `pre-commit` + simple script).

---

## Troubleshooting

| Issue                                   | Cause                                | Fix                                                                                     |
| --------------------------------------- | ------------------------------------ | --------------------------------------------------------------------------------------- |
| `ModuleNotFoundError: backend` in tests | Path not injected early              | Ensure `tests/conftest.py` executes sys.path insertion before imports (already handled) |
| Empty /api/solutions/index              | No solutions directory found         | Run `build_solutions.py` or verify `APP_SOLUTIONS_DIR`                                  |
| Frontend fetch errors                   | Backend not running or CORS mismatch | Start backend on port 8000; confirm allowed origin                                      |
| Null language blocks                    | Single-language filter applied       | Use `lang=both` to retrieve both                                                        |

---

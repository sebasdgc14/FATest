from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


# Example: expose the parsed JSON files (if you want)
@app.get("/api/requirements")
def get_requirements():
    import json
    import pathlib

    p = pathlib.Path(__file__).resolve().parents[1] / "requirements.json"
    if not p.exists():
        return {"error": "requirements.json not found"}
    return json.loads(p.read_text(encoding="utf-8"))

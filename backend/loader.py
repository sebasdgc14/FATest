from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class LoadError:
    kind: str  # e.g. "not_found", "invalid_json"
    detail: str


JsonData = Any  # We only lightly validate (list root for current datasets)


def load_json(path: Path) -> tuple[JsonData | None, LoadError | None]:
    """Pure JSON file loader.

    Returns a tuple of (data, error). Never raises. All filesystem and
    JSON parsing side-effects are contained here so that callers can
    translate domain/file errors into HTTP responses at the boundary.
    """
    if not path.exists():
        return None, LoadError("not_found", f"{path.name} not found")
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:  # IO error
        return None, LoadError("io_error", f"Failed reading {path.name}: {e}")
    try:
        return json.loads(text), None
    except json.JSONDecodeError as e:
        return None, LoadError("invalid_json", f"Invalid JSON in {path.name}: {e}")

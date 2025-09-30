import json
import os
from pathlib import Path

from Normalizing import load_yaml_sequence, parse_solutions

SCRIPT_ROOT = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_ROOT.parents[1]

# Allow overrides via environment variables for portability
RAW_SOLUTIONS_DIR = Path(
    os.getenv("RAW_SOLUTIONS_DIR", REPO_ROOT / "data" / "raw" / "solutions_yaml")
)
OUT_DIR = Path(
    os.getenv("SOLUTIONS_OUTPUT_DIR", REPO_ROOT / "data" / "solutions" / "solutions_json")
)

OUT_DIR.mkdir(parents=True, exist_ok=True)


def build_all() -> list[str]:
    written = []
    if not RAW_SOLUTIONS_DIR.exists():
        print(f"[WARN] Source solutions YAML directory missing: {RAW_SOLUTIONS_DIR}")
        return written
    for yaml_path in RAW_SOLUTIONS_DIR.glob("*.yaml"):
        try:
            data = load_yaml_sequence(str(yaml_path))
        except Exception as e:
            print(f"[SKIP] {yaml_path.name}: {e}")
            continue
        solutions = parse_solutions(data)
        out_path = OUT_DIR / (yaml_path.stem + ".json")
        out_path.write_text(json.dumps(solutions, ensure_ascii=False, indent=2), encoding="utf-8")
        written.append(out_path.name)
        print(f"[OK] {yaml_path.name} -> {out_path.relative_to(Path.cwd())}")
    return written


if __name__ == "__main__":
    produced = build_all()
    print(f"Generated {len(produced)} solution JSON file(s).")

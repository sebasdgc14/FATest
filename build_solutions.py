import json
from pathlib import Path
from typing import List
from test import load_yaml_sequence, parse_solutions

SRC_DIR = Path(__file__).parent / "solutions_yaml"
OUT_DIR = Path(__file__).parent / "solutions_json"

OUT_DIR.mkdir(exist_ok=True)


def build_all() -> List[str]:
    written = []
    for yaml_path in SRC_DIR.glob("*.yaml"):
        try:
            data = load_yaml_sequence(str(yaml_path))
        except Exception as e:
            print(f"[SKIP] {yaml_path.name}: {e}")
            continue
        solutions = parse_solutions(data)
        out_path = OUT_DIR / (yaml_path.stem + ".json")
        out_path.write_text(
            json.dumps(solutions, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        written.append(out_path.name)
        print(f"[OK] {yaml_path.name} -> {out_path.relative_to(Path.cwd())}")
    return written


if __name__ == "__main__":
    produced = build_all()
    print(f"Generated {len(produced)} solution JSON file(s).")

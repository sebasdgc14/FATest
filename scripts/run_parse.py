import json
import os
from pathlib import Path

from Normalizing import (
    load_yaml_mapping,
    parse_compliance,
    parse_requirements,
    parse_vulnerabilities,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = Path(os.getenv("RAW_CORE_DIR", REPO_ROOT / "data" / "raw"))
CORE_OUT = Path(os.getenv("CORE_OUTPUT_DIR", REPO_ROOT / "data" / "core"))
CORE_OUT.mkdir(parents=True, exist_ok=True)

# Helper to load a raw YAML mapping with clearer error messages
def load_raw(name: str):
    path = RAW_DIR / name
    return load_yaml_mapping(str(path))

# ----------------------
# Requirements data
# ----------------------
data = load_raw("requirements_data.yaml")
reqs = parse_requirements(data)

print("Parsed requirement items:", len(reqs))
# Print the first requirement item for inspection
if reqs:
    print(json.dumps(reqs[0], ensure_ascii=False, indent=2))

# Persist full JSON to a file for further inspection
req_out = CORE_OUT / "requirements.json"
req_out.write_text(json.dumps(reqs, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Wrote {req_out.relative_to(REPO_ROOT)}")


# ----------------------
# Compliance data (test block)
# ----------------------
try:
    c_data = load_raw("compliance_data.yaml")
    comp = parse_compliance(c_data)

    print("\nParsed compliance items:", len(comp))
    # Print the first compliance entry for inspection
    if comp:
        print(json.dumps(comp[0], ensure_ascii=False, indent=2))

    # Persist compliance JSON for inspection
    c_out = CORE_OUT / "compliance.json"
    c_out.write_text(json.dumps(comp, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {c_out.relative_to(REPO_ROOT)}")
except FileNotFoundError:
    print("compliance_data.yaml not found; skipping compliance test block.")

# ----------------------
# Vulnerability data (test block)
# ----------------------
try:
    v_data = load_raw("vulnerabilities_data.yaml")
    vuln = parse_vulnerabilities(v_data)

    print("\nParsed vulnerability items:", len(vuln))
    # Print the first vulnerability entry for inspection
    if vuln:
        print(json.dumps(vuln[0], ensure_ascii=False, indent=2))

    # Persist vulnerability JSON for inspection
    v_out = CORE_OUT / "vulnerabilities.json"
    v_out.write_text(json.dumps(vuln, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {v_out.relative_to(REPO_ROOT)}")
except FileNotFoundError:
    print("vulnerabilities_data.yaml not found; skipping vulnerability test block.")

from test import (
    load_yaml_mapping,
    load_yaml_sequence,
    parse_requirements,
    parse_compliance,
    parse_vulnerabilities,
    parse_solutions,
)
import json
from pathlib import Path

# ----------------------
# Requirements data
# ----------------------
data = load_yaml_mapping("requirements_data.yaml")
reqs = parse_requirements(data)

print("Parsed requirement items:", len(reqs))
# Print the first requirement item for inspection
if reqs:
    print(json.dumps(reqs[0], ensure_ascii=False, indent=2))

# Persist full JSON to a file for further inspection
Path("requirements.json").write_text(
    json.dumps(reqs, ensure_ascii=False, indent=2), encoding="utf-8"
)
print("Wrote requirements.json")


# ----------------------
# Compliance data (test block)
# ----------------------
try:
    c_data = load_yaml_mapping("compliance_data.yaml")
    comp = parse_compliance(c_data)

    print("\nParsed compliance items:", len(comp))
    # Print the first compliance entry for inspection
    if comp:
        print(json.dumps(comp[0], ensure_ascii=False, indent=2))

    # Persist compliance JSON for inspection
    Path("compliance.json").write_text(
        json.dumps(comp, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Wrote compliance.json")
except FileNotFoundError:
    print("compliance_data.yaml not found; skipping compliance test block.")

# ----------------------
# Vulnerability data (test block)
# ----------------------
try:
    v_data = load_yaml_mapping("vulnerabilities_data.yaml")
    vuln = parse_vulnerabilities(v_data)

    print("\nParsed vulnerability items:", len(vuln))
    # Print the first vulnerability entry for inspection
    if vuln:
        print(json.dumps(vuln[0], ensure_ascii=False, indent=2))

    # Persist vulnerability JSON for inspection
    Path("vulnerabilities.json").write_text(
        json.dumps(vuln, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Wrote vulnerabilities.json")
except FileNotFoundError:
    print("vulnerabilities_data.yaml not found; skipping vulnerability test block.")


# ----------------------
# Solutions data (test block)
# ----------------------
try:
    s_data = load_yaml_sequence("solutions_android.yaml")
    sols = parse_solutions(s_data)

    print("\nParsed solution items:", len(sols))
    # Print the first solutions entry for inspection
    if sols:
        print(json.dumps(sols[0], ensure_ascii=False, indent=2))

    # Persist solutions JSON for inspection
    Path("solutions_android.json").write_text(
        json.dumps(sols, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("Wrote solutions_android.json")
except FileNotFoundError:
    print("v=solutions_android.yaml not found; skipping solutions test block.")

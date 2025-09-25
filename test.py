from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml


def yaml_safe_load(text: str) -> Any:
    """
    We use safe_load to only produce basic, safe Python types.
    General structure of the .yaml files ensures it will be
    converted into dictionaries due to the key:value structure.

    Args:
        text: the YAML document as a string

    Returns:
        The parsed Python object, if parsing doesn't
        work then an empty dictionary is returned
    """
    return yaml.safe_load(text) or {}


def load_yaml_mapping(path: str) -> Dict[str, Any]:
    """
    Explicit loader that guarantees the returned value is a mapping (dict).

    This preserves the original strict behaviour but exposes it via a
    clearly named function so callers can choose strict mapping-only loading.
    """
    route = Path(path).read_text(encoding="utf-8")
    data = yaml_safe_load(route)
    if not isinstance(data, dict):
        raise ValueError(f"YAML root must be a mapping (dict): {path}")
    return data


def load_yaml_sequence(path: str) -> List[Any]:
    """
    Explicit loader that guarantees the returned value is a sequence (list).

    Use this for files that are expected to be top-level YAML sequences,
    such as `solutions_android.yaml` in this workspace.
    """
    route = Path(path).read_text(encoding="utf-8")
    data = yaml_safe_load(route)
    if not isinstance(data, list):
        raise ValueError(f"YAML root must be a sequence (list): {path}")
    return data


def ensure_str(a: Any, default: str = "") -> str:
    """
    This will ensure that all entries will be converted into
    str for consistency's sake. Handling even None values into
    a default one.

    Args:
        a: a python object of Any type.
        default: str default for when a is None.

    Returns:
        A string representation of the given value or the default for None.
    """
    if a is None:
        return default
    return str(a)


def ensure_list_of_str(x: Any) -> List[str]:
    if x is None:
        return []
    return [ensure_str(el) for el in x] if isinstance(x, list) else [ensure_str(x)]


#############################################################################
# Normalizing all types of yaml files
#############################################################################


def normalize_requirements(rid: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Given the shape of the requirements yaml lets give it a set structure.

    'Id' and 'category' are str.
    'en' and 'es' are mappings that contain 'title', 'summary', 'description'.
    'supported in' is a mapping of booleans or None
    'references' is a list of strings
    'metadata' is a dictionary
    'last_update_time' becomes str o a None

    Args:
        rid: the requirement YAML identifier (str)
        raw: the raw payload parsed from the YAML file for this requirement. (Dict)

    Returns:
        A normalized dict.
    """
    # In case something is wrong with raw, let's make it an empty dict
    raw = raw or {}
    # There are localization versions so let's give them the same treatment
    en = raw.get("en") or {}
    es = raw.get("es") or {}
    supported_in = raw.get("supported_in") or {}
    # Refs is a list, rather than a dict
    refs = raw.get("references") or []
    if not isinstance(refs, list):
        refs = [refs]  # this handles a single entry becoming a str
    build = {
        "id": ensure_str(rid),
        "en": {
            "title": ensure_str(en.get("title")),
            "summary": ensure_str(en.get("summary")),
            "description": ensure_str(en.get("description")),
        },
        "es": {
            "title": ensure_str(es.get("title")),
            "summary": ensure_str(es.get("summary")),
            "description": ensure_str(es.get("description")),
        },
        "category": ensure_str(raw.get("category")),
        "supported_in": (
            {
                "essential": supported_in.get("essential", None),
                "advanced": supported_in.get("advanced", None),
            }
            if supported_in
            else None
        ),
        "references": [ensure_str(x) for x in refs],
        "metadata": raw.get("metadata", {}),
        "last_update_time": ensure_str(raw.get("last_update_time"))
        if raw.get("last_update_time") is not None
        else None,
    }
    return build


def normalize_compliance(name: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize one top-level compliance entry (e.g. 'capec', 'bsimm').

    Expected input shape:
      - title: string
      - en: { summary: ... }
      - es: { summary: ... }
      - definitions: mapping of id -> { title, link }
      - metadata: dict
      - last_update_time: string

    Output shape is a predictable dict with these keys:
      - id: top-level key name (e.g. 'capec')
      - title
      - en_summary, es_summary
      - definitions: list of { id, title, link }
      - metadata
      - last_update_time
    """
    # In case something is wrong with raw, let's make it an empty dict
    raw = raw or {}
    # Ensuring strings and dictionaries
    title = ensure_str(raw.get("title"))
    en = raw.get("en") or {}
    es = raw.get("es") or {}
    en_summary = ensure_str(en.get("summary"))
    es_summary = ensure_str(es.get("summary"))

    defs = raw.get("definitions") or {}
    definitions_list: List[Dict[str, Any]] = []

    # definitions is usually a mapping id -> {title, link}
    if isinstance(defs, dict):
        for did, dval in defs.items():
            if isinstance(dval, dict):
                dtitle = ensure_str(dval.get("title"))
                dlink = (
                    ensure_str(dval.get("link"))
                    if dval.get("link") is not None
                    else None
                )
            else:
                # fallback: treat scalar as title
                dtitle = ensure_str(dval)
                dlink = None
            definitions_list.append(
                {"id": ensure_str(did), "title": dtitle, "link": dlink}
            )

    last = (
        ensure_str(raw.get("last_update_time"))
        if raw.get("last_update_time") is not None
        else None
    )

    build = {
        "id": ensure_str(name),
        "title": title,
        "en_summary": en_summary,
        "es_summary": es_summary,
        "definitions": definitions_list,
        "metadata": raw.get("metadata", {}),
        "last_update_time": last,
    }
    return build


def normalize_vulnerability(rid: str, raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single vulnerability entry.

    Output shape (all keys always present, values may be None):
      {
        id: str,
        en: { title, description, impact, recommendation, threat },
        es: { title, description, impact, recommendation, threat },
        category: str,
        examples: { non_compliant, compliant } | None,
        remediation_time: str | None,
        score: { base: {...} | None, temporal: {...} | None } | None,
        score_v4: { base: {...} | None, threat: {...} | None } | None,
        requirements: [str, ...],
        metadata: dict,
        last_update_time: str | None
      }
    """
    raw = raw or {}
    en = raw.get("en") or {}
    es = raw.get("es") or {}

    # Define a language block to avoid repetitive code
    def _lang_block(block: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "title": ensure_str(block.get("title")),
            "description": ensure_str(block.get("description")),
            "impact": ensure_str(block.get("impact")),
            "recommendation": ensure_str(block.get("recommendation")),
            "threat": ensure_str(block.get("threat")),
        }

    # Treating the example block structure
    ex = raw.get("examples") or {}
    examples = None
    if isinstance(ex, dict) and (ex.get("non_compliant") or ex.get("compliant")):
        examples = {
            "non_compliant": ensure_str(ex.get("non_compliant")),
            "compliant": ensure_str(ex.get("compliant")),
        }

    # Score block
    score_raw = raw.get("score") or {}
    score_base_raw = score_raw.get("base") or {}
    score_temporal_raw = score_raw.get("temporal") or {}
    score_base = None
    if score_base_raw:
        score_base = {
            "attack_vector": ensure_str(score_base_raw.get("attack_vector")),
            "attack_complexity": ensure_str(score_base_raw.get("attack_complexity")),
            "privileges_required": ensure_str(
                score_base_raw.get("privileges_required")
            ),
            "user_interaction": ensure_str(score_base_raw.get("user_interaction")),
            "scope": ensure_str(score_base_raw.get("scope")),
            "confidentiality": ensure_str(score_base_raw.get("confidentiality")),
            "integrity": ensure_str(score_base_raw.get("integrity")),
            "availability": ensure_str(score_base_raw.get("availability")),
        }
    score_temporal = None
    if score_temporal_raw:
        score_temporal = {
            "exploit_code_maturity": ensure_str(
                score_temporal_raw.get("exploit_code_maturity")
            ),
            "remediation_level": ensure_str(
                score_temporal_raw.get("remediation_level")
            ),
            "report_confidence": ensure_str(
                score_temporal_raw.get("report_confidence")
            ),
        }
    score: Optional[Dict[str, Any]] = None
    if score_base or score_temporal:
        score = {"base": score_base, "temporal": score_temporal}

    # Score v4 block
    score4_raw = raw.get("score_v4") or {}
    score4_base_raw = score4_raw.get("base") or {}
    score4_threat_raw = score4_raw.get("threat") or {}
    score4_base = None
    if score4_base_raw:
        score4_base = {
            "attack_vector": ensure_str(score4_base_raw.get("attack_vector")),
            "attack_complexity": ensure_str(score4_base_raw.get("attack_complexity")),
            "attack_requirements": ensure_str(
                score4_base_raw.get("attack_requirements")
            ),
            "privileges_required": ensure_str(
                score4_base_raw.get("privileges_required")
            ),
            "user_interaction": ensure_str(score4_base_raw.get("user_interaction")),
            "confidentiality_vc": ensure_str(score4_base_raw.get("confidentiality_vc")),
            "integrity_vi": ensure_str(score4_base_raw.get("integrity_vi")),
            "availability_va": ensure_str(score4_base_raw.get("availability_va")),
            "confidentiality_sc": ensure_str(score4_base_raw.get("confidentiality_sc")),
            "integrity_si": ensure_str(score4_base_raw.get("integrity_si")),
            "availability_sa": ensure_str(score4_base_raw.get("availability_sa")),
        }
    score4_threat = None
    if score4_threat_raw:
        score4_threat = {
            "exploit_maturity": ensure_str(score4_threat_raw.get("exploit_maturity")),
        }
    score_v4: Optional[Dict[str, Any]] = None
    if score4_base or score4_threat:
        score_v4 = {"base": score4_base, "threat": score4_threat}

    # Requirements list
    reqs = raw.get("requirements") or []
    if not isinstance(reqs, list):
        reqs = [reqs]
    requirements = [ensure_str(r) for r in reqs]

    # Metadata block
    metadata_raw = raw.get("metadata") or {}
    en_metadata = metadata_raw.get("en") or {}
    en_metadata_details = ensure_str(en_metadata.get("details"))

    # building
    build = {
        "id": ensure_str(rid),
        "en": _lang_block(en),
        "es": _lang_block(es),
        "category": ensure_str(raw.get("category")),
        "examples": examples,
        "remediation_time": ensure_str(raw.get("remediation_time"))
        if raw.get("remediation_time") is not None
        else None,
        "score": score,
        "score_v4": score_v4,
        "requirements": requirements,
        "metadata": {"en": {"details": en_metadata_details}},
        "last_update_time": ensure_str(raw.get("last_update_time"))
        if raw.get("last_update_time") is not None
        else None,
    }
    return build


def normalize_solutions(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize a single solutions entry.

    Output shape (modified order for better readability):
      {
        "vulnerability_id": str,
        "title": str,
        "context": [str, ...],
        "need": str,
        "solution":{
            "language": str,
            "insecure_code_example": {"description": str, "text": str},
            "secure_code_example": {"description": str, "text": str},
            "steps": [str, ...]
        },
        "last_update_time": str | None
      }
    """
    raw = raw or {}
    vuln_id = ensure_str(raw.get("vulnerability_id") or "")
    title = ensure_str(raw.get("title") or "")
    context = ensure_list_of_str(raw.get("context"))
    need = ensure_str(raw.get("need"))
    # Now for the example structures
    solution = raw.get("solution") or {}

    def code_example(name: str, sol: Dict):
        b = sol.get(name) or {}
        return {
            "description": ensure_str(b.get("description")),
            "text": ensure_str(b.get("text")),
        }

    insecure = code_example("insecure_code_example", solution)
    secure = code_example("secure_code_example", solution)
    language = ensure_str(solution.get("language") or "")
    steps = ensure_list_of_str(solution.get("steps"))
    last = (
        ensure_str(raw["last_update_time"])
        if raw.get("last_update_time") is not None
        else None
    )

    build = {
        "vulnerability_id": vuln_id,
        "title": title,
        "context": context,
        "need": need,
        "solution": {
            "language": language,
            "insecure_code_example": insecure,
            "secure_code_example": secure,
            "steps": steps,
        },
        "last_update_time": last,
    }
    return build


#############################################################################
# parsing all normalized files
#############################################################################


def parse_requirements(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the full requirements mapping into a list of normalized entries.
    """
    items: List[Dict[str, Any]] = []
    for rid, raw in doc.items():
        if isinstance(raw, dict):
            items.append(normalize_requirements(str(rid), raw))
    return items


def parse_compliance(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Parse the full compliance mapping into a list of normalized entries.

    This mirrors `parse_requirements` but for the compliance file's shape.
    """
    items: List[Dict[str, Any]] = []
    for name, raw in doc.items():
        if isinstance(raw, dict):
            items.append(normalize_compliance(str(name), raw))
    return items


def parse_vulnerabilities(doc: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Parse full vulnerabilities mapping into a list of normalized entries."""
    items: List[Dict[str, Any]] = []
    for vid, raw in doc.items():
        if isinstance(raw, dict):
            items.append(normalize_vulnerability(str(vid), raw))
    return items


def parse_solutions(doc: Any) -> List[Dict[str, Any]]:
    """Parse full solutions input into a list of normalized entries.

    Supports both mapping (id -> entry) and list-of-entries YAML shapes.
    For mapping inputs the key is ignored because each entry contains its
    own `vulnerability_id` field. For list inputs entries are processed in
    order.
    """
    items: List[Dict[str, Any]] = []
    # if isinstance(doc, dict):
    #    for _, raw in doc.items():
    #       if isinstance(raw, dict):
    #            items.append(normalize_solutions(raw))
    if isinstance(doc, list):
        for raw in doc:
            if isinstance(raw, dict):
                items.append(normalize_solutions(raw))
    return items


##################################################################
# tools
#############################################################################


def count_ids_in_yaml(path: str) -> int:
    """Return the number of top-level requirement IDs in a YAML file.

    This function reuses `load_yaml_file` which already validates the YAML
    root is a mapping and returns a Python dict. We then return the length of
    that mapping, which corresponds to how many requirement entries (IDs)
    are present.

    Args:
        path: Path to the YAML file.

    Returns:
        Integer count of top-level keys (IDs) in the YAML mapping.
    """
    data = load_yaml_mapping(path)
    # load_yaml_file guarantees `data` is a dict (or raises), so simply return len
    return len(data)

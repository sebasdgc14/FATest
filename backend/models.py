from typing import Any

from pydantic import BaseModel


# --------------------
# Requirements models
# --------------------
class RequirementLang(BaseModel):
    title: str
    summary: str
    description: str


class RequirementOut(BaseModel):
    id: str
    category: str | None
    en: RequirementLang | None = None
    es: RequirementLang | None = None
    supported_in: dict[str, bool | None] | None
    references: list[str]
    metadata: dict[str, Any]
    last_update_time: str | None


# --------------------
# Compliance models
# --------------------
class ComplianceDefinition(BaseModel):
    id: str
    title: str
    link: str | None = None


class ComplianceLang(BaseModel):
    summary: str | None = None


class ComplianceOut(BaseModel):
    id: str
    title: str
    en: ComplianceLang | None = None
    es: ComplianceLang | None = None
    definitions: list[ComplianceDefinition]
    metadata: dict[str, Any]
    last_update_time: str | None


# --------------------
# Vulnerability models
# --------------------
class VulnerabilityLang(BaseModel):
    title: str
    description: str
    impact: str
    recommendation: str
    threat: str


class VulnerabilityExamples(BaseModel):
    non_compliant: str | None = None
    compliant: str | None = None


class VulnerabilityScoreBase(BaseModel):
    attack_vector: str | None = None
    attack_complexity: str | None = None
    privileges_required: str | None = None
    user_interaction: str | None = None
    scope: str | None = None
    confidentiality: str | None = None
    integrity: str | None = None
    availability: str | None = None


class VulnerabilityScoreTemporal(BaseModel):
    exploit_code_maturity: str | None = None
    remediation_level: str | None = None
    report_confidence: str | None = None


class VulnerabilityScore(BaseModel):
    base: VulnerabilityScoreBase | None = None
    temporal: VulnerabilityScoreTemporal | None = None


class VulnerabilityScoreV4Base(BaseModel):
    attack_vector: str | None = None
    attack_complexity: str | None = None
    attack_requirements: str | None = None
    privileges_required: str | None = None
    user_interaction: str | None = None
    confidentiality_vc: str | None = None
    integrity_vi: str | None = None
    availability_va: str | None = None
    confidentiality_sc: str | None = None
    integrity_si: str | None = None
    availability_sa: str | None = None


class VulnerabilityScoreV4Threat(BaseModel):
    exploit_maturity: str | None = None


class VulnerabilityScoreV4(BaseModel):
    base: VulnerabilityScoreV4Base | None = None
    threat: VulnerabilityScoreV4Threat | None = None


class VulnerabilityOut(BaseModel):
    id: str
    category: str | None
    en: VulnerabilityLang | None = None
    es: VulnerabilityLang | None = None
    examples: VulnerabilityExamples | None = None
    remediation_time: str | None = None
    score: VulnerabilityScore | None = None
    score_v4: VulnerabilityScoreV4 | None = None
    requirements: list[str]
    metadata: dict[str, Any]
    last_update_time: str | None


# --------------------
# Solutions models
# --------------------
class SolutionCodeExample(BaseModel):
    description: str | None = None
    text: str | None = None


class SolutionDetails(BaseModel):
    language: str | None = None
    insecure_code_example: SolutionCodeExample = SolutionCodeExample()
    secure_code_example: SolutionCodeExample = SolutionCodeExample()
    steps: list[str] = []


class SolutionOut(BaseModel):
    vulnerability_id: str
    title: str
    context: list[str]
    need: str
    solution: SolutionDetails
    last_update_time: str | None = None


# --------------------
# Solutions index models
# --------------------
class SolutionsIndexItem(BaseModel):
    name: str
    count: int | None = None
    error: str | None = None


class SolutionsIndexOut(BaseModel):
    datasets: list[SolutionsIndexItem]

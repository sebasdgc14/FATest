from typing import List, Optional, Dict, Any
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
    category: Optional[str]
    en: Optional[RequirementLang] = None
    es: Optional[RequirementLang] = None
    supported_in: Optional[Dict[str, Optional[bool]]]
    references: List[str]
    metadata: Dict[str, Any]
    last_update_time: Optional[str]


# --------------------
# Compliance models
# --------------------
class ComplianceDefinition(BaseModel):
    id: str
    title: str
    link: Optional[str] = None


class ComplianceLang(BaseModel):
    summary: Optional[str] = None


class ComplianceOut(BaseModel):
    id: str
    title: str
    en: Optional[ComplianceLang] = None
    es: Optional[ComplianceLang] = None
    definitions: List[ComplianceDefinition]
    metadata: Dict[str, Any]
    last_update_time: Optional[str]


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
    non_compliant: Optional[str] = None
    compliant: Optional[str] = None


class VulnerabilityScoreBase(BaseModel):
    attack_vector: Optional[str] = None
    attack_complexity: Optional[str] = None
    privileges_required: Optional[str] = None
    user_interaction: Optional[str] = None
    scope: Optional[str] = None
    confidentiality: Optional[str] = None
    integrity: Optional[str] = None
    availability: Optional[str] = None


class VulnerabilityScoreTemporal(BaseModel):
    exploit_code_maturity: Optional[str] = None
    remediation_level: Optional[str] = None
    report_confidence: Optional[str] = None


class VulnerabilityScore(BaseModel):
    base: Optional[VulnerabilityScoreBase] = None
    temporal: Optional[VulnerabilityScoreTemporal] = None


class VulnerabilityScoreV4Base(BaseModel):
    attack_vector: Optional[str] = None
    attack_complexity: Optional[str] = None
    attack_requirements: Optional[str] = None
    privileges_required: Optional[str] = None
    user_interaction: Optional[str] = None
    confidentiality_vc: Optional[str] = None
    integrity_vi: Optional[str] = None
    availability_va: Optional[str] = None
    confidentiality_sc: Optional[str] = None
    integrity_si: Optional[str] = None
    availability_sa: Optional[str] = None


class VulnerabilityScoreV4Threat(BaseModel):
    exploit_maturity: Optional[str] = None


class VulnerabilityScoreV4(BaseModel):
    base: Optional[VulnerabilityScoreV4Base] = None
    threat: Optional[VulnerabilityScoreV4Threat] = None


class VulnerabilityOut(BaseModel):
    id: str
    category: Optional[str]
    en: Optional[VulnerabilityLang] = None
    es: Optional[VulnerabilityLang] = None
    examples: Optional[VulnerabilityExamples] = None
    remediation_time: Optional[str] = None
    score: Optional[VulnerabilityScore] = None
    score_v4: Optional[VulnerabilityScoreV4] = None
    requirements: List[str]
    metadata: Dict[str, Any]
    last_update_time: Optional[str]


# --------------------
# Solutions models
# --------------------
class SolutionCodeExample(BaseModel):
    description: Optional[str] = None
    text: Optional[str] = None


class SolutionDetails(BaseModel):
    language: Optional[str] = None
    insecure_code_example: SolutionCodeExample = SolutionCodeExample()
    secure_code_example: SolutionCodeExample = SolutionCodeExample()
    steps: List[str] = []


class SolutionOut(BaseModel):
    vulnerability_id: str
    title: str
    context: List[str]
    need: str
    solution: SolutionDetails
    last_update_time: Optional[str] = None

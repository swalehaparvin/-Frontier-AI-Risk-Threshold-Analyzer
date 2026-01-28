from pydantic import BaseModel
from typing import List, Optional


class RiskTier(BaseModel):
    tier_name: str
    tier_level: int
    capability_threshold: str
    compute_threshold_flops: Optional[float] = None
    evaluation_requirements: List[str] = []
    required_safeguards: List[str] = []


class Framework(BaseModel):
    organization: str
    framework_name: str
    risk_tiers: List[RiskTier]


class ModelSpecs(BaseModel):
    name: str
    training_compute_flops: float
    parameters: Optional[float] = None
    passed_evaluations: List[str] = []
    capabilities: List[str] = []


class RiskAssessment(BaseModel):
    model_name: str
    framework_assessments: dict  # {framework_name: tier_name}
    eu_compliant: bool
    eu_requirements: List[str] = []
    gaps_identified: List[str] = []

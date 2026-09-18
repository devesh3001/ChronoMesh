from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class InferredState(str, Enum):
    no_significant_event = "no_significant_event"
    new_child_life_event = "new_child_life_event"
    marriage_or_relationship_change = "marriage_or_relationship_change"
    job_change_or_promotion = "job_change_or_promotion"
    job_loss_or_income_disruption = "job_loss_or_income_disruption"
    medical_hardship = "medical_hardship"
    financial_distress_general = "financial_distress_general"
    relocation = "relocation"
    retirement_transition = "retirement_transition"
    wealth_growth_or_windfall = "wealth_growth_or_windfall"
    potential_fraud_or_takeover = "potential_fraud_or_takeover"
    elder_vulnerability_or_scam_risk = "elder_vulnerability_or_scam_risk"
    churn_risk = "churn_risk"
    small_business_cashflow_event = "small_business_cashflow_event"

class Action(str, Enum):
    no_action = "no_action"
    proactive_retention_outreach = "proactive_retention_outreach"
    relationship_manager_escalation = "relationship_manager_escalation"
    personalized_offer = "personalized_offer"
    support_intervention = "support_intervention"
    compliance_fraud_hold = "compliance_fraud_hold"

class HitlStatus(str, Enum):
    auto_approved = "auto_approved"
    escalated = "escalated"
    human_approved = "human_approved"
    human_rejected = "human_rejected"
    human_modified = "human_modified"

class ConfidenceBand(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Checkpoint(BaseModel):
    as_of_time: datetime
    inferred_state: InferredState
    confidence_band: ConfidenceBand
    action: Action
    action_subtype: Optional[str] = None
    hitl_status: HitlStatus
    notes: Optional[str] = None

class EvidenceContract(BaseModel):
    evidence_id: str
    customer_id: str
    claim_type: str
    structured_value: str
    source_role: str
    confidence: ConfidenceBand
    source_event_ids: List[str]
    valid_from: datetime
    valid_to: Optional[datetime] = None
    superseded_by: Optional[str] = None

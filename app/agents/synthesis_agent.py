import os
from typing import List
from app.db.repository import EvidenceRecord
from app.models.state import InferredState, ConfidenceBand

class SynthesisAgent:
    """
    Reconciles findings from all agents into a coherent customer state.
    """
    def __init__(self):
        self.use_llm = "OPENAI_API_KEY" in os.environ

    def synthesize(self, customer_id: str, evidence: List[dict]) -> dict:
        state = InferredState.no_significant_event
        confidence = ConfidenceBand.low
        
        # 1. Aggregate Evidence
        large_withdrawals = [e for e in evidence if e["claim_type"] == "large_outbound_transfer"]
        dissatisfactions = [e for e in evidence if e["claim_type"] == "support_dissatisfaction"]
        
        # 2. LLM Synthesis (Mocked if no key)
        if self.use_llm:
            # Here we would use LangChain's structured output parser
            # to feed the evidence into an LLM and parse the exact InferredState enum.
            # prompt = f"Given this evidence: {evidence}, determine the state."
            pass
            
        # Fallback Synthesis Rules
        if len(large_withdrawals) > 0 and len(dissatisfactions) > 0:
            # Strong signal: They were mad at support AND withdrew money
            state = InferredState.churn_risk
            confidence = ConfidenceBand.high
            notes = "Synthesized: High churn risk due to correlated support dissatisfaction and large withdrawal."
        elif len(large_withdrawals) > 0:
            # Weak signal: Only withdrew money, could be a normal transfer
            state = InferredState.churn_risk
            confidence = ConfidenceBand.medium
            notes = "Synthesized: Medium churn risk due to large withdrawal without supporting negative signals."
        elif len(dissatisfactions) > 0:
            # Weak signal: Mad at support, but haven't moved money yet
            state = InferredState.churn_risk
            confidence = ConfidenceBand.low
            notes = "Synthesized: Low churn risk. Support dissatisfaction logged, monitoring for capital flight."
        else:
            notes = "Synthesized: No significant life events detected."
            
        return {
            "inferred_state": state,
            "confidence_band": confidence,
            "notes": notes
        }

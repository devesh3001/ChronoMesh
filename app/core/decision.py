from app.models.state import InferredState, Action, HitlStatus, ConfidenceBand

class DecisionEngine:
    def calculate_utility(self, action_cost: float, expected_retention_value: float, confidence: ConfidenceBand) -> float:
        """
        Dynamic cost/benefit utility calculator.
        """
        confidence_multiplier = {"low": 0.2, "medium": 0.6, "high": 0.95}
        # Expected value = (Probability of success * Value) - Cost
        # Simplified for prototype
        utility = (expected_retention_value * confidence_multiplier[confidence]) - action_cost
        return utility

    def decide(self, synthesis_result: dict) -> dict:
        state = synthesis_result["inferred_state"]
        confidence = synthesis_result["confidence_band"]
        
        action = Action.no_action
        hitl_status = HitlStatus.auto_approved
        action_subtype = None
        
        if state == InferredState.churn_risk:
            # Evaluate candidates
            # Option A: Do nothing (Cost: 0, Retention: 0) -> Utility: 0
            # Option B: Proactive Retention Outreach (Cost: $50, Retention: $500)
            utility_b = self.calculate_utility(50, 500, confidence)
            # Option C: Relationship Manager Escalation (Cost: $200, Retention: $1000)
            utility_c = self.calculate_utility(200, 1000, confidence)
            
            best_utility = max(0, utility_b, utility_c)
            
            if best_utility == utility_c and best_utility > 0:
                action = Action.relationship_manager_escalation
                action_subtype = "premium_retention_offer_and_fee_waiver"
                # High cost actions require HITL
                hitl_status = HitlStatus.escalated if confidence != ConfidenceBand.high else HitlStatus.auto_approved
                # Wait, the PS says any costly/customer-facing action needs real checkpoint.
                # Let's enforce HITL for ALL relationship manager escalations or personalized offers.
                hitl_status = HitlStatus.escalated
            elif best_utility == utility_b and best_utility > 0:
                action = Action.proactive_retention_outreach
                action_subtype = "standard_retention_email"
                hitl_status = HitlStatus.auto_approved
            
        return {
            "action": action,
            "action_subtype": action_subtype,
            "hitl_status": hitl_status
        }

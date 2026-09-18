from app.models.events import BaseEvent
from typing import List

class TransactionAgent:
    """
    Analyzes transaction/billing events and creates evidence contracts.
    """
    def __init__(self):
        pass
        
    def process(self, event: BaseEvent) -> List[dict]:
        evidence_contracts = []
        
        # Example logic for scenario_03: Churn Risk
        if event.source_system == "instant_payments" and event.event_type == "outbound_transfer":
            payload = event.payload
            amount = payload.get("amount", 0.0)
            
            if amount > 5000:
                # Large withdrawal is a flag for potential churn or relocation
                contract = {
                    "evidence_id": f"ev_{event.event_id}",
                    "customer_id": event.customer_id,
                    "claim_type": "large_outbound_transfer",
                    "structured_value": "high_withdrawal_activity",
                    "source_role": "transaction_agent",
                    "confidence": "high",
                    "source_event_ids": [event.event_id],
                    "valid_from": event.event_time,
                    "valid_to": None,
                    "superseded_by": None
                }
                evidence_contracts.append(contract)
                
        # More robust logic for other systems can be added here
        return evidence_contracts

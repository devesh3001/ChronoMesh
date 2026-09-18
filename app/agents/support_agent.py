import os
from typing import List
from app.models.events import BaseEvent

# In a real setup, we would use LangChain's ChatOpenAI here.
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import PromptTemplate

class SupportAgent:
    """
    Analyzes unstructured support logs and extracts evidence contracts.
    """
    def __init__(self):
        self.use_llm = "OPENAI_API_KEY" in os.environ
        
    def process(self, event: BaseEvent) -> List[dict]:
        evidence_contracts = []
        
        if event.source_system == "support_logs":
            raw_text = event.payload.get("raw_text", "").lower()
            resolution = event.payload.get("resolution_status", "")
            
            # Simulated LLM parsing
            if self.use_llm:
                # LLM logic would go here:
                # llm = ChatOpenAI(temperature=0)
                # result = llm.invoke(f"Extract intent and sentiment from: {raw_text}")
                pass
            
            # Fallback heuristic parsing for demonstration
            if "fee" in raw_text and "waive" in raw_text and resolution == "human_rejected":
                evidence_contracts.append({
                    "evidence_id": f"ev_{event.event_id}",
                    "customer_id": event.customer_id,
                    "claim_type": "support_dissatisfaction",
                    "structured_value": "fee_waiver_denied",
                    "source_role": "support_agent",
                    "confidence": "high",
                    "source_event_ids": [event.event_id],
                    "valid_from": event.event_time,
                    "valid_to": None,
                    "superseded_by": None
                })
                
        return evidence_contracts

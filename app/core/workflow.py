import operator
from typing import TypedDict, Annotated, List, Any, Optional
from langgraph.graph import StateGraph, END
from app.models.events import BaseEvent
from app.db.database import SessionLocal
from app.db.repository import save_evidence, get_current_evidence, save_checkpoint
from app.agents.transaction_agent import TransactionAgent
from app.agents.support_agent import SupportAgent
from app.agents.synthesis_agent import SynthesisAgent
from app.core.decision import DecisionEngine

# Define the state for the LangGraph
class AgentState(TypedDict):
    event: BaseEvent
    evidence_contracts: List[dict]
    current_evidence: List[Any]
    synthesis_result: dict
    decision: dict
    final_output: dict

def extract_evidence(state: AgentState):
    """Node: Extract evidence from the raw event"""
    t_agent = TransactionAgent()
    s_agent = SupportAgent()
    
    contracts = t_agent.process(state["event"])
    contracts.extend(s_agent.process(state["event"]))
    
    # Save to our temporal DB
    db = SessionLocal()
    try:
        for contract in contracts:
            save_evidence(db, contract)
        
        # Retrieve the current valid state of the board
        current_evidence_records = get_current_evidence(db, state["event"].customer_id, state["event"].event_time)
        current_evidence = [
            {
                "claim_type": r.claim_type,
                "structured_value": r.structured_value,
                "confidence": r.confidence,
            } for r in current_evidence_records
        ]
    finally:
        db.close()
        
    return {"evidence_contracts": contracts, "current_evidence": current_evidence}

def synthesize_state(state: AgentState):
    """Node: Synthesize the current customer state"""
    # Only synthesize if there's actual evidence
    if not state.get("current_evidence"):
        return {"synthesis_result": {}}
        
    agent = SynthesisAgent()
    result = agent.synthesize(state["event"].customer_id, state["current_evidence"])
    return {"synthesis_result": result}

def make_decision(state: AgentState):
    """Node: Decide on the bounded action"""
    if not state.get("synthesis_result"):
        return {"decision": {}}
        
    engine = DecisionEngine()
    decision = engine.decide(state["synthesis_result"])
    return {"decision": decision}

def route_decision(state: AgentState) -> str:
    """Conditional Edge: Route to HITL or direct execution"""
    decision = state.get("decision", {})
    if not decision:
        return "end"
        
    if decision.get("hitl_status") == "escalated":
        return "human_in_the_loop"
    return "execute_action"

def human_in_the_loop(state: AgentState):
    """Node: A placeholder node where execution will be interrupted"""
    # In LangGraph, we can use a breakpoint *before* a node to pause. 
    # Or, we can use the new `interrupt()` feature.
    # Here, we will just return the state; we will set a breakpoint BEFORE this node in the graph compilation.
    return state

def execute_action(state: AgentState):
    """Node: Execute the action and export the checkpoint"""
    decision = state.get("decision", {})
    synthesis = state.get("synthesis_result", {})
    event = state.get("event")
    
    if not decision or not synthesis:
        return {"final_output": None}
        
    # We might have received updated instructions from the human during the pause
    # (e.g. human changed hitl_status to 'human_approved')
    # For now, we just construct the final output.
    
    checkpoint_data = {
        "as_of_time": event.event_time,
        "inferred_state": synthesis["inferred_state"],
        "confidence_band": synthesis["confidence_band"],
        "notes": synthesis["notes"],
        **decision
    }
    
    db = SessionLocal()
    try:
        save_checkpoint(db, checkpoint_data, event.customer_id)
    finally:
        db.close()
        
    return {"final_output": checkpoint_data}

def create_workflow():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("extract_evidence", extract_evidence)
    workflow.add_node("synthesize_state", synthesize_state)
    workflow.add_node("make_decision", make_decision)
    workflow.add_node("human_in_the_loop", human_in_the_loop)
    workflow.add_node("execute_action", execute_action)
    
    # Edges
    workflow.set_entry_point("extract_evidence")
    workflow.add_edge("extract_evidence", "synthesize_state")
    workflow.add_edge("synthesize_state", "make_decision")
    
    workflow.add_conditional_edges(
        "make_decision",
        route_decision,
        {
            "human_in_the_loop": "human_in_the_loop",
            "execute_action": "execute_action",
            "end": END
        }
    )
    
    # After HITL, we execute
    workflow.add_edge("human_in_the_loop", "execute_action")
    workflow.add_edge("execute_action", END)
    
    return workflow

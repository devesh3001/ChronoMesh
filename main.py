import os
import sqlite3
from datetime import datetime
from langgraph.checkpoint.sqlite import SqliteSaver

from app.db.database import engine, SessionLocal
from app.db.repository import init_db
from app.core.ingestion import stream_events_ordered
from app.core.exporter import Exporter
from app.core.workflow import create_workflow

def run_scenario(live_stream_path: str, output_path: str):
    init_db(engine)
    exporter = Exporter(output_path)
    
    print(f"Starting pipeline on {live_stream_path}")
    
    # Initialize the sqlite checkpointer for LangGraph
    conn = sqlite3.connect("langgraph_checkpoints.db", check_same_thread=False)
    checkpointer = SqliteSaver(conn)
    
    # Create and compile the workflow
    workflow = create_workflow()
    # We compile the graph with the checkpointer and set an interrupt BEFORE the 'human_in_the_loop' node
    app = workflow.compile(checkpointer=checkpointer, interrupt_before=["human_in_the_loop"])
    
    # Process events
    for i, event in enumerate(stream_events_ordered(live_stream_path)):
        # Every run needs a unique thread ID for LangGraph to track state
        # In a real system, the thread_id might be the customer_id + a session/ticket ID.
        thread_id = f"thread_{event.customer_id}_{event.event_id}"
        config = {"configurable": {"thread_id": thread_id}}
        
        initial_state = {
            "event": event,
            "evidence_contracts": [],
            "current_evidence": [],
            "synthesis_result": {},
            "decision": {},
            "final_output": {}
        }
        
        # Run the graph
        for output in app.stream(initial_state, config, stream_mode="updates"):
            # You can log node transitions here if desired
            pass
            
        # Check if the graph paused (interrupted)
        state_info = app.get_state(config)
        
        if state_info.next and "human_in_the_loop" in state_info.next:
            decision = state_info.values.get("decision", {})
            print(f"--> [LANGGRAPH INTERRUPT] Pausing execution for {event.customer_id}.")
            print(f"--> Action escalated: {decision.get('action')}")
            
            # Simulate a human coming back hours later and clicking "Approve"
            # We update the state to mark it as human approved
            print("--> [HUMAN INPUT] Human approved.")
            decision["hitl_status"] = "human_approved"
            app.update_state(config, {"decision": decision})
            
            # Resume the graph from the breakpoint
            for output in app.stream(None, config, stream_mode="updates"):
                pass
                
        # Get final state to export
        final_state = app.get_state(config).values
        if final_state.get("final_output"):
            exporter.add_checkpoint(final_state["final_output"])

    exporter.save()
    conn.close()
    print(f"Finished pipeline. Exported {len(exporter.checkpoints)} checkpoints to {output_path}")

if __name__ == "__main__":
    scenario_file = "dataset_extracted/scenario_03/live_stream.jsonl"
    out_file = "scenario_03_output.json"
    
    if os.path.exists("c360_mesh.db"):
        os.remove("c360_mesh.db")
    if os.path.exists("langgraph_checkpoints.db"):
        os.remove("langgraph_checkpoints.db")
        
    run_scenario(scenario_file, out_file)

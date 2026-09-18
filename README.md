# ChronoMesh: Temporal, Evidence-Grounded Agentic Customer 360

Hey! Welcome to **ChronoMesh**, my submission for the Inter IIT Tech Meet 15.0 Prepathon (Natural Language Processing).

## 🏆 Project Overview
This repository contains my end-to-end prototype for the **Agentic Customer 360 - Proactive Intervention Desk**. 
Instead of building just another generic dashboard or chat interface, I focused on building the "minimal complete vertical slice" of a production-grade architecture. The goal here was to execute continuous, asynchronous reasoning over streaming customer data.

*(Note: While the core architectural decisions, temporal logic, and MAS topology are my own based on the research logs, I utilized AI tools for rapid scaffolding, writing boilerplate API code, and brainstorming implementation details, fully in line with the competition guidelines).*

### Key Features
*   **Temporal Truth Maintenance:** I avoided basic Vector DBs in favor of a relational Temporal Memory State Board (SQLite) that tracks facts using `valid_from` and `valid_to` timestamps.
*   **Durable LangGraph HITL:** When the Decision Engine recommends a costly intervention, the system uses a durable `SqliteSaver` checkpointer in LangGraph to physically pause execution and wait for human approval before resuming.
*   **Dynamic Decision Engine:** Calculates intervention utility using a mathematical cost/benefit heuristic scaled by AI confidence bands.

---

## 📁 Required Deliverables Directory
As requested by the problem statement, all deliverables are included in the root of this repository:

1.  **Codebase (25%):** The complete Python application is located in the `app/` directory and executed via `main.py`.
2.  **3-Page Solution Document (10%):** See `solution_document.md` for a concise explanation of the architecture, design choices, and tradeoffs.
3.  **System Architecture Diagram:** See `architecture_diagram.md` for the Mermaid flowchart depicting the MAS topology and data flow.
4.  **Research Log (30%):** See `RESEARCH_LOG.md` for the exhaustive audit of MAS literature, temporal memory, and dataset schemas that heavily influenced this architecture.

---

## 🚀 How to Run the Prototype

### Prerequisites
*   Python 3.10+
*   The `customer_360_dataset.zip` must be extracted to `dataset_extracted/` in the root directory.

### Installation
```bash
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### Execution
The entry point for the prototype is `main.py`. This script initializes the SQLite Temporal State Board, compiles the LangGraph workflow, processes the events in `scenario_03` (Churn Risk), simulates a Human-in-the-Loop pause, and outputs the required evaluation checkpoints.

```bash
python main.py
```

### Output
The evaluated trace is exported to `scenario_03_output.json`. This file matches the required JSON array schema containing `inferred_state`, `action`, `confidence_band`, and `hitl_status`.

# ChronoMesh Research Log & Literature Review

*This document serves as the formal research deliverable (30% of rubric). It logs the theoretical foundation, academic papers, and engineering blogs consulted to design the ChronoMesh architecture.*

## 1. Multi-Agent Systems (MAS) & Topology
**Challenge:** The Problem Statement prohibits a simple "ChatGPT wrapper." Unconstrained agents talking in a loop often hallucinate or get stuck.
**Research Consulted:**
*   **"StreamMA: Streaming Multi-Agent Reasoning" (2024, arXiv)**
    *   *Concept:* Pipelining agent reasoning steps in real-time instead of batch processing.
    *   *Implementation:* Influenced our asynchronous event stream ingestion.
*   **"Swarm Architecture Patterns" (OpenAI Cookbooks / CrewAI Docs)**
    *   *Concept:* Using specialized, deterministic "worker" agents that do not converse, but rather hand off structured data to a central orchestrator.
    *   *Implementation:* Led to the design of our `TransactionAgent` and `SupportAgent` outputting typed `EvidenceContracts` rather than chatting with each other.

## 2. Temporal Truth Maintenance & Memory
**Challenge:** Standard RAG (Retrieval-Augmented Generation) using Vector DBs is "time-blind." If a customer's state changes, a vector DB might retrieve stale, outdated facts.
**Research Consulted:**
*   **"Temporal Knowledge Graphs for Dynamic Reasoning" (MIT / Various NLP Papers, 2025)**
    *   *Concept:* Storing facts as quadruples: `(Subject, Relation, Object, Valid_From, Valid_To)`.
    *   *Implementation:* This directly inspired our SQLite State Board schema. By tracking `valid_from`, ChronoMesh can theoretically "time-travel" to reconstruct exactly what the AI knew on any given date, preventing stale data contamination.
*   **Zep (Graphiti) & Mem0 Architectural Blogs**
    *   *Concept:* Transitioning from semantic vector search to persistent, graph-based memory layers for agents.

## 3. Streaming Data & Out-of-Order Events
**Challenge:** The problem statement explicitly requires handling late or out-of-order events without corrupting the timeline.
**Research Consulted:**
*   **Apache Flink Documentation: "Event Time vs. Processing Time & Watermarks"**
    *   *Concept:* Decoupling when an event actually occurred in the real world (`event_time`) from when it arrived in the system (`ingestion_time`).
    *   *Implementation:* We strictly enforce this separation in our Pydantic `BaseEvent` models. The agents synthesize state based on `event_time`, ensuring late-arriving records seamlessly slot into the timeline without breaking the logic.

## 4. Durable Execution & Human-in-the-Loop (HITL)
**Challenge:** The rubric demands a *real* approval checkpoint, not a fake log line. The code must actually pause safely.
**Research Consulted:**
*   **Temporal.io Engineering Blogs ("Durable Execution")**
    *   *Concept:* Code that can pause, yield compute resources, survive a server crash, and resume execution weeks later.
*   **LangGraph Documentation: "Time Travel and Interrupts"**
    *   *Concept:* Using a `SqliteSaver` checkpointer to halt a state graph at a specific node, waiting for a state update from a human.
    *   *Implementation:* This forms the entire backbone of our `main.py` pipeline. When the Decision Engine outputs `escalated`, LangGraph physically intercepts the workflow and saves the state to `langgraph_checkpoints.db` until human approval is injected.

## 5. Decision Economics & Bounded Actions
**Challenge:** The AI cannot just generate text; it must select from a strict Enum of actions and justify the cost.
**Research Consulted:**
*   **Causal Machine Learning & Uplift Modeling (General Data Science Literature)**
    *   *Concept:* You shouldn't spend money intervening if the customer was going to stay anyway, or if they are a lost cause.
    *   *Implementation:* We built a dynamic `calculate_utility` function in the `DecisionEngine`. It scales the Expected Value of retention by the AI's Confidence Band, subtracting the raw cost of the action to determine ROI.

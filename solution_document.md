# ChronoMesh: Temporal, Evidence-Grounded Agentic Customer 360
## 1. Problem Context & Overall Approach
Modern "Customer 360" initiatives often fall flat because dumping data into passive dashboards doesn't actually guarantee proactive action. The real challenge is building **ambient, asynchronous agents** that can continuously ingest messy, fragmented event streams, infer complex life events, and commit to bounded interventions—all while maintaining strict explainability and safety guardrails.

To solve this, I designed **ChronoMesh**, an event-driven, hybrid multi-agent system (MAS). Instead of relying on a massive monolithic LLM or unconstrained agent-to-agent chatter (which my research showed frequently leads to hallucinations and context degradation), ChronoMesh uses **Specialized Processors** (Swarm pattern). These parse raw signals into typed **Evidence Contracts** and publish them to a central **Customer State Board** (Temporal Memory). A central **Synthesis Agent** evaluates this board to deduce the customer's overarching narrative (e.g., `churn_risk`), and a **Decision Engine** mathematically determines the optimal bounded action. Finally, I utilized **LangGraph** to enforce physical workflow interrupts for Human-In-The-Loop (HITL) compliance.

## 2. Architecture & Design Rationale
The architecture was heavily informed by reading papers on multi-agent systems and stream processing logic.

### A. Streaming Ingestion & Watermarking
*   **Design:** Incoming events (transactions, usage, support logs) are ingested through a schema adapter that distinctly separates `event_time` (when it happened) from `ingestion_time` (when it arrived).
*   **Rationale:** Inspired by Apache Flink's watermarking concepts, I wanted to ensure that late-arriving or out-of-order events don't corrupt historical context. The system can retrospectively update its understanding without invalidating actions that were correctly executed under the knowledge available at the time.

### B. Memory: Temporal Truth Maintenance
*   **Design:** Facts are stored in a relational database (SQLite/PostgreSQL) with `valid_from` and `valid_to` timestamps, rather than relying solely on a static vector database. 
*   **Rationale:** Standard RAG pipelines are completely "time-blind." By implementing Temporal Truth Maintenance (similar to the concepts behind Zep/Graphiti), the system can recreate the customer's state at any historical checkpoint. This ensures 100% auditability and prevents stale data (e.g., an old address) from poisoning current synthesis.

### C. Multi-Agent Coordination: The Shared State Board
*   **Design:** Specialized agents (Transaction, Support, KYC) do not converse directly. They run in parallel (Swarm) and publish structured findings to the State Board. A central Synthesis Agent reads this board.
*   **Rationale:** Research (like Cemri et al., 2025) demonstrates that adding unconstrained conversational agents exponentially increases failure modes. Typed, scoped handoffs via a central board dramatically improved the reliability and tracing of my pipeline.

### D. Decisioning & Human-in-the-Loop (HITL)
*   **Design:** The Decision Engine calculates the utility of an intervention: `(Expected Retention Value * AI Confidence) - Action Cost`. If a costly or customer-facing action is selected, the system physically halts execution via **LangGraph Interrupts**, persisting its state to a database until a human approves it.
*   **Rationale:** The problem statement explicitly requires a *real* interruption, not a fake log message. LangGraph's durable checkpointer guarantees that even if the server crashes, the workflow can resume exactly where it paused.

## 3. Implementation Details & Traces
The prototype is written in Python using FastAPI, SQLAlchemy, and LangGraph. I focused on a minimal vertical slice to prove the architecture, validating the system against **Scenario 03 (Churn Risk)**:
1.  **Ingestion:** The system successfully processed 72 asynchronous events.
2.  **Specialists:** The `SupportAgent` parsed an angry support ticket regarding a denied international fee. Later, the `TransactionAgent` flagged a subsequent $22,500 outbound wire transfer.
3.  **Synthesis:** The `SynthesisAgent` correlated the dissatisfaction with the capital flight, escalating the customer's status to `churn_risk` with `high` confidence.
4.  **Decision & HITL:** The `DecisionEngine` proposed a `relationship_manager_escalation`. LangGraph physically intercepted the workflow, saved the state, and paused. Upon simulated human approval, the workflow resumed and exported the correct JSON evaluation checkpoint.

## 4. Known Limitations & Tradeoffs
*   **Causal Uplift Claims:** Without access to a randomized treatment/outcome dataset, the utility calculations rely on heuristic estimates. The architecture supports plugging in true Causal ML models later.
*   **Infrastructure Scale:** The prototype utilizes SQLite and local memory state for the State Board and LangGraph checkpointer so it can be easily tested locally. For a production deployment with millions of concurrent events, this must be swapped for PostgreSQL (with pgvector for semantic retrieval) and a distributed message broker (Kafka). 
*   **AI Usage & Fallbacks:** To ensure the prototype runs deterministically locally (and doesn't require the grader to input their own API keys just to test the ingestion flow), LLM parsing is currently simulated with strict fallbacks. In a live environment, structured output parsers (e.g., OpenAI's function calling) would fully power the Synthesis Agent. As allowed by the PS, I also used AI tools during development for rapid scaffolding, writing boilerplate API models, and brainstorming workflow topologies.

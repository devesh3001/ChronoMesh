# C360-Mesh System Architecture

Below is the definitive system architecture diagram for the C360-Mesh implementation. It highlights the flow of data, the strict boundaries between agents, the Temporal Truth Maintenance database, and the explicit LangGraph human-in-the-loop pause mechanism.

```mermaid
flowchart TD
    %% Define Data Sources
    subgraph Data Sources [Asynchronous Event Streams]
        U[Usage/Web App]
        S[Support/Chat]
        T[Transactions/Billing]
        K[KYC/Compliance]
    end

    %% Ingestion Layer
    subgraph Ingestion Layer
        I[Schema Adapter & Dedup]
        W[Watermarking & Lateness Handler]
        L[(Append-Only Event Log)]
        I --> W --> L
    end
    U & S & T & K --> I

    %% Deterministic Guardrails
    G[Hard-Stop Guardrails\nLegal / Fraud Rules]
    L --> G

    %% Specialized Swarm Agents (Parallel)
    subgraph Specialists [Specialized Signal Agents]
        UA[Usage Agent]
        SA[Support Agent]
        TA[Transaction Agent]
        KA[KYC Agent]
    end
    L --> UA & SA & TA & KA

    %% Temporal Memory (State Board)
    subgraph Memory [Temporal Memory / Shared State Board]
        DB[(PostgreSQL / SQLite)]
        TM[Temporal Truth Maintenance\nvalid_from / valid_to]
        WM[Working Memory\ncurrent active case]
        DB --- TM
        DB --- WM
    end
    
    %% Agents write structured evidence to DB
    UA & SA & TA & KA --"Publishes Evidence Contracts"--> DB

    %% Synthesis & Correlation
    subgraph Synthesis [Synthesis & Correlation]
        SYN[Synthesis Agent\nLLM Reconciler]
    end
    DB --"Reads scoped facts"--> SYN

    %% Decision & Verification
    subgraph Decision Layer
        DE[Decision Engine\nUtility & Cost Calculator]
        VR[Verifier/Debate\nTriggered only on conflict]
    end
    SYN --"Proposes Inferred State"--> DE
    SYN -.->|If material conflict| VR -.-> DE
    G -.->|Bypasses LLM on violation| DE

    %% Execution & HITL (LangGraph)
    subgraph Execution & HITL [LangGraph Orchestrator]
        R{Risk / Ambiguity Level}
        EXEC[Execute Autonomous Action]
        PAUSE((LangGraph HITL Checkpoint))
        HUMAN[@Human Approver]
        
        DE --> R
        R -->|Low Risk & Cost| EXEC
        R -->|Costly or Ambiguous| PAUSE
        PAUSE <-->|Wait for Input| HUMAN
        HUMAN -->|Approved/Modified| EXEC
    end

    %% Output
    OUT[JSON Inferred-Event Output\nEvaluation Format]
    EXEC --> OUT

    %% Styling
    classDef memory fill:#d4edda,stroke:#28a745,stroke-width:2px;
    classDef hitl fill:#f8d7da,stroke:#dc3545,stroke-width:2px;
    classDef agent fill:#cce5ff,stroke:#007bff,stroke-width:2px;
    classDef source fill:#fff3cd,stroke:#ffc107,stroke-width:2px;

    class DB,TM,WM memory;
    class PAUSE,HUMAN hitl;
    class UA,SA,TA,KA,SYN agent;
    class U,S,T,K source;
```

## Diagram Key Design Choices
1.  **Strict Handoffs:** Notice that the Specialized Agents (Usage, Support, Transaction) do *not* point directly to the Synthesis Agent. They point to the Shared State Board. This prevents conversational context pollution.
2.  **Synchronous vs. Asynchronous:** The core event log processing and specialized agent ingestion is fully asynchronous. The Synthesis and Decision loops are triggered upon material changes to the State Board.
3.  **Durable Pause:** The `LangGraph HITL Checkpoint` is not merely a conditional logic branch; it is an orchestrator node that physically persists state to the database and halts execution, yielding resources until human intervention occurs.

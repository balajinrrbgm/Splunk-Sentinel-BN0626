# Architecture Diagram

```mermaid
graph TB
    subgraph "Data Sources"
        A[Splunk Enterprise/Cloud]
        A --> B[Security Events<br/>Authentication, Firewall, IDS]
        A --> C[Network Logs<br/>DNS, NetFlow, Proxy]
        A --> D[System Metrics<br/>CPU, Memory, Disk]
    end

    subgraph "Splunk AI Layer"
        E[Splunk MCP Server<br/>Model Context Protocol]
        G[Foundation-Sec-1.1-8B-Instruct<br/>Security LLM]
        I[Cisco Deep Time Series Model<br/>Anomaly Detection]
        K[Python SDK AI<br/>Agentic Workflows]
        M[AI Assistant<br/>Natural Language → SPL]
    end

    subgraph "SplunkSentinel Agent Pipeline"
        O[🎯 Orchestrator Agent<br/>Pipeline Coordinator]
        P[🔍 Triage Agent<br/>Alert Scoring & Priority]
        Q[🕵️ Investigation Agent<br/>Deep Correlation]
        R[⏱️ Timeline Agent<br/>Kill Chain Reconstruction]
        S[📊 Forecast Agent<br/>Anomaly Prediction]
        T[🛡️ Response Agent<br/>Remediation Playbooks]
        
        O --> P
        O --> Q
        O --> R
        O --> S
        O --> T
    end

    subgraph "Frontend Dashboard"
        U[React Dashboard<br/>Real-time SOC Interface]
        V[Alert Feed<br/>Live Streaming]
        W[Investigation Panel<br/>AI Analysis Viewer]
        X[Timeline View<br/>Attack Visualization]
        Y[Anomaly Forecast<br/>Predictive Charts]
        Z[Response Actions<br/>Playbook Generator]
        
        U --> V
        U --> W
        U --> X
        U --> Y
        U --> Z
    end

    B --> E
    C --> E
    D --> E
    
    E --> O
    G --> Q
    G --> T
    I --> S
    K --> P
    M --> Q
    
    O -->|WebSocket Stream| U

    style O fill:#00d4ff,stroke:#0a0e1a,color:#0a0e1a
    style P fill:#2ecc71,stroke:#0a0e1a,color:#0a0e1a
    style Q fill:#a855f7,stroke:#0a0e1a,color:#fff
    style R fill:#ff9f43,stroke:#0a0e1a,color:#0a0e1a
    style S fill:#3498db,stroke:#0a0e1a,color:#fff
    style T fill:#ff4757,stroke:#0a0e1a,color:#fff
    style U fill:#0a0e1a,stroke:#00d4ff,color:#e5e7eb
```

## Data Flow

1. **Ingest** — Security events from Splunk flow through the MCP Server into SplunkSentinel
2. **Triage** — Triage Agent uses Foundation-Sec to score and prioritize alerts by severity
3. **Investigate** — Investigation Agent queries Splunk for correlated evidence across indexes
4. **Timeline** — Timeline Agent reconstructs the complete attack kill chain
5. **Forecast** — Forecast Agent uses Cisco DTSM to predict future anomaly windows
6. **Respond** — Response Agent generates tailored remediation playbooks with SPL queries
7. **Visualize** — React dashboard displays all agent outputs in real-time via WebSocket

# 🛡️🤖 SplunkSentinel

### AI-Powered Autonomous SOC Analyst — From Alert Storm to Actionable Intelligence in Seconds

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-green.svg)](https://python.org)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://reactjs.org)

---

## 🚨 The Problem

**SOC teams are drowning.**

- **4,484 alerts per day** — average for enterprise SOC teams (Palo Alto Networks, 2024)
- **67% of alerts are ignored** — analysts can't keep up with the volume
- **197 days** — mean time to detect a data breach (IBM Cost of a Data Breach, 2024)
- **$4.88 million** — average cost of a data breach
- **78% of SOC analysts** experience burnout (Tines State of Mental Health in Cybersecurity, 2024)

The alert storm isn't a technology problem — it's an **intelligence problem**. Raw alerts lack context, correlation, and actionable guidance. Analysts spend 80% of their time on manual triage that an AI system could handle in seconds.

---

## 💡 The Solution

**SplunkSentinel** deploys 5 specialized AI agents that work together as an autonomous SOC analyst, transforming raw Splunk security data into prioritized, investigated, and actionable intelligence — in real-time.

Built on Splunk's complete AI ecosystem, SplunkSentinel demonstrates the future of Security Operations: **human-AI collaboration where agents handle the noise and analysts focus on decisions.**

---

## ✨ Key Features

- 🔍 **Intelligent Alert Triage** — AI scores and prioritizes thousands of alerts in seconds using Foundation-Sec reasoning
- 🕵️ **Autonomous Investigation** — Agents correlate events across multiple Splunk indexes automatically
- ⏱️ **Attack Timeline Reconstruction** — Visualize the complete kill chain with MITRE ATT&CK mapping
- 📊 **Anomaly Forecasting** — Predict future threats using Cisco Deep Time Series Model
- 🛡️ **Response Recommendations** — AI-generated remediation playbooks with executable SPL queries
- 🔌 **Splunk MCP Integration** — Secure, protocol-compliant connection to all Splunk data
- 🧠 **Foundation-Sec Reasoning** — Security-specialized LLM for expert-level threat analysis
- ⚡ **Real-time Dashboard** — Premium SOC interface with WebSocket-powered live updates
- 🤖 **Multi-Agent Architecture** — 5 coordinated agents with streaming status visibility

---

## 🏗️ Architecture

![SplunkSentinel Architecture](architecture.png)

*See [architecture.md](architecture.md) for the full Mermaid diagram source.*

### Agent Pipeline Flow

```
┌─────────────┐    ┌──────────────┐    ┌────────────────┐    ┌──────────────┐    ┌───────────────┐
│  🔍 TRIAGE  │───▶│ 🕵️ INVESTIGATE│───▶│ ⏱️ TIMELINE    │───▶│ 📊 FORECAST  │───▶│ 🛡️ RESPOND   │
│   Agent     │    │    Agent      │    │    Agent       │    │    Agent     │    │    Agent      │
├─────────────┤    ├──────────────┤    ├────────────────┤    ├──────────────┤    ├───────────────┤
│ Score alerts│    │ Query Splunk  │    │ Reconstruct    │    │ Predict next │    │ Generate      │
│ Prioritize  │    │ Correlate     │    │ kill chain     │    │ anomalies    │    │ playbooks     │
│ Deduplicate │    │ Map ATT&CK    │    │ Map entities   │    │ Risk windows │    │ SPL queries   │
└─────────────┘    └──────────────┘    └────────────────┘    └──────────────┘    └───────────────┘
```

---

## 🔧 Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Backend | Python 3.11+, FastAPI | Agent orchestration server |
| Frontend | React 18, Vite | Real-time SOC dashboard |
| AI Models | Foundation-Sec-1.1-8B, Cisco DTSM | Security reasoning & forecasting |
| Integration | Splunk MCP Server | Secure Splunk data access |
| SDK | Splunk Python SDK AI | Agentic alert workflows |
| Assistant | Splunk AI Assistant | Natural language SPL generation |
| Deployment | Docker Compose | One-command setup |

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose **(recommended path)**
- For local development without Docker:
  - Python **3.11+** and `pip`
  - Node.js **18+** and `npm`
- (Optional) Splunk Enterprise/Cloud instance with MCP Server enabled

### One-Command Setup

```bash
# Clone the repository
git clone https://github.com/your-team/splunk-sentinel.git
cd splunk-sentinel

# Copy environment config
cp .env.example .env

# Launch everything (demo mode — no Splunk required!)
docker-compose up --build
```

### Access the Dashboard

- **Frontend Dashboard**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### Demo Mode

SplunkSentinel includes a full **demo mode** that runs without a live Splunk instance — perfect for evaluation. It loads realistic sample security data and simulates the complete agent pipeline with streaming updates.

```bash
# Explicitly enable demo mode
DEMO_MODE=true docker-compose up
```

---

## 🛠️ Local Development (Without Docker)

Prefer to run the services directly? Start the backend and frontend in two separate terminals.

### 1. Backend (FastAPI)

```bash
cd backend

# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment config from the repo root (or export vars manually)
cp ../.env.example .env

# Run the API (defaults to demo mode)
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 2. Frontend (React + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

The dashboard will be available at http://localhost:5173 and will connect to the backend at http://localhost:8000.

---

## 📦 Dependencies

All dependencies are declared in version-pinned manifests:

| Component | Manifest | Key packages |
|-----------|----------|--------------|
| Backend | [`backend/requirements.txt`](backend/requirements.txt) | FastAPI, Uvicorn, Pydantic, splunk-sdk, httpx, websockets, structlog |
| Frontend | [`frontend/package.json`](frontend/package.json) | React 18, Vite, @vitejs/plugin-react |
| Splunk App | Splunk Python SDK AI runtime | Alert actions & modular inputs (see [`splunk_app/`](splunk_app/)) |

---

## ⚙️ Environment Configuration

Copy [`.env.example`](.env.example) to `.env` and adjust as needed. In **demo mode**, no Splunk or model endpoints are required — sane defaults are used everywhere.

| Variable | Default | Description |
|----------|---------|-------------|
| `SPLUNK_HOST` | `localhost` | Splunk management host |
| `SPLUNK_PORT` | `8089` | Splunk management port |
| `SPLUNK_TOKEN` | _(empty)_ | Splunk auth token (only needed for live mode) |
| `SPLUNK_MCP_ENDPOINT` | `http://localhost:8088/mcp` | Splunk MCP Server endpoint |
| `FOUNDATION_SEC_ENDPOINT` | _(empty)_ | Foundation-Sec model endpoint (live mode) |
| `CISCO_DTSM_ENDPOINT` | _(empty)_ | Cisco Deep Time Series Model endpoint (live mode) |
| `BACKEND_PORT` | `8000` | Backend API port |
| `FRONTEND_PORT` | `5173` | Frontend dashboard port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `DEMO_MODE` | `true` | Run with bundled sample data — no live Splunk required |

---

## 🗃️ Sample Datasets

Demo mode is powered by realistic, ready-to-use security datasets in [`backend/sample_data/`](backend/sample_data):

| File | Contents |
|------|----------|
| [`sample_alerts.json`](backend/sample_data/sample_alerts.json) | Prioritized security alerts (brute force, SQL injection, lateral movement, etc.) with severity, source IPs, hosts, and MITRE-relevant fields |
| [`security_events.json`](backend/sample_data/security_events.json) | Raw security events used for investigation and timeline correlation |
| [`network_traffic.json`](backend/sample_data/network_traffic.json) | Network flow data used by the Forecast Agent for anomaly prediction |

These datasets let evaluators run the complete agent pipeline end-to-end without connecting a live Splunk instance.

---

## 🎬 Demo Video

▶️ [Watch the 3-minute demo on YouTube](https://youtube.com/watch?v=PLACEHOLDER)

---

## 🧠 Splunk AI Capabilities Used

SplunkSentinel leverages **ALL 5** Splunk AI capabilities:

| Capability | How It's Used |
|-----------|---------------|
| **Splunk MCP Server** | Core data connector — all Splunk queries flow through MCP for secure, protocol-compliant access |
| **Foundation-Sec-1.1-8B-Instruct** | Security reasoning engine for alert triage, investigation analysis, and response generation |
| **Cisco Deep Time Series Model** | Anomaly forecasting — predicts future threat windows from historical patterns |
| **Python SDK AI** | Splunk app component with custom alert actions and modular inputs for agentic workflows |
| **AI Assistant** | SPL query generation from natural language investigation questions |

---

## 🔍 How It Works

### 1. Ingest
Splunk security events (authentication logs, firewall events, IDS alerts, network flows) are accessed via the **Splunk MCP Server**, providing secure and structured data access.

### 2. Triage (Triage Agent)
The Triage Agent pulls raw alerts and uses **Foundation-Sec** to:
- Classify severity (Critical/High/Medium/Low/Info)
- Calculate composite threat scores using MITRE ATT&CK mapping
- De-duplicate and correlate related alerts
- Output a prioritized investigation queue

### 3. Investigate (Investigation Agent)
For high-priority alerts, the Investigation Agent:
- Generates SPL queries using **AI Assistant** integration
- Queries across multiple Splunk indexes (main, _audit, network)
- Uses **Foundation-Sec** to reason about attack patterns
- Produces investigation reports with evidence and confidence scores

### 4. Timeline (Timeline Agent)
The Timeline Agent reconstructs the attack narrative:
- Correlates events across time windows
- Maps to MITRE ATT&CK kill chain stages
- Identifies: Initial Access → Lateral Movement → Exfiltration
- Generates entity relationship graphs

### 5. Forecast (Forecast Agent)
The Forecast Agent uses the **Cisco Deep Time Series Model** to:
- Predict anomalies in network traffic, auth failures, DNS patterns
- Distinguish seasonal patterns from true anomalies
- Generate risk windows with confidence intervals

### 6. Respond (Response Agent)
The Response Agent generates actionable playbooks:
- Immediate actions (block IP, disable accounts)
- Short-term mitigations (firewall updates, credential rotation)
- Long-term fixes (patch vulnerabilities, update detection rules)
- Each response includes executable SPL queries

### 7. Visualize (React Dashboard)
Everything streams to the dashboard in real-time via WebSocket:
- Live alert feed with severity indicators
- Investigation progress with agent status
- Attack timeline visualization
- Anomaly forecast charts
- Response action cards

---

## 💬 Sample Queries

SplunkSentinel can answer questions like:

- *"What are the top critical threats right now?"*
- *"Investigate the brute force attack on server-prod-01"*
- *"Show me the attack timeline for alert ALT-2024-1337"*
- *"Predict anomalies in network traffic for the next 24 hours"*
- *"Generate a response playbook for the lateral movement detected"*

---

## 📂 Project Structure

```
splunk-sentinel/
├── backend/              # FastAPI agent orchestration server
│   ├── agents/           # 5 specialized AI agents
│   ├── connectors/       # Splunk MCP + hosted model clients
│   ├── models/           # Data models
│   ├── services/         # SPL generation, reports
│   └── sample_data/      # Demo datasets
├── frontend/             # React + Vite SOC dashboard
│   └── src/
│       ├── components/   # Dashboard UI components
│       └── utils/        # API client
├── splunk_app/           # Splunk app (Python SDK AI)
│   ├── bin/              # Alert actions & modular inputs
│   └── default/          # Splunk configurations
├── docker-compose.yml    # One-command deployment
└── architecture.md       # System architecture diagram
```

---

## 🗺️ Future Roadmap

- [ ] **SOAR Integration** — Direct integration with Splunk SOAR for automated response execution
- [ ] **Multi-tenant Support** — Serve multiple SOC teams with isolated agent pipelines
- [ ] **Custom Agent Training** — Fine-tune Foundation-Sec on organization-specific threat patterns
- [ ] **Compliance Reporting** — Auto-generate SOC 2, HIPAA, PCI-DSS compliance reports
- [ ] **Threat Hunting Mode** — Proactive agent that hunts for hidden threats
- [ ] **Collaborative Investigation** — Multiple analysts working with AI agents simultaneously

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a pull request.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

*Built with ❤️ using Splunk AI, Foundation-Sec, and the power of autonomous agents.*

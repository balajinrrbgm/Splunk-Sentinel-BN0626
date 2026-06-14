# 🛡️ SplunkSentinel — Hackathon Submission

## ⚡ Elevated Pitch (≤200 characters)

> **5 AI agents that act as an autonomous SOC analyst — turning thousands of raw Splunk alerts into prioritized, investigated, and actionable threat intelligence in seconds, not hours.**

*(193 characters)*

---

## Inspiration

SOC teams are drowning. The average enterprise security team faces **4,484
alerts per day**, ignores **67% of them** out of sheer volume, and still takes
**197 days** to detect a breach — at an average cost of **$4.88 million**.
Meanwhile **78% of analysts report burnout**, grinding through manual triage
that eats 80% of their day.

We realized the alert storm isn't a data problem — Splunk already collects the
data. It's an **intelligence problem**: raw alerts lack context, correlation,
and a clear next action. So we asked: what if a team of specialized AI agents
could do the triage, investigation, and response planning automatically, and
let human analysts focus only on the decisions that matter?

## What it does

SplunkSentinel deploys **5 specialized AI agents** that work together as an
autonomous SOC analyst, transforming raw Splunk security data into prioritized,
investigated, and actionable intelligence in real time:

- 🔍 **Triage Agent** — scores and prioritizes thousands of alerts in seconds using Foundation-Sec reasoning and MITRE ATT&CK mapping; deduplicates and correlates related alerts.
- 🕵️ **Investigation Agent** — auto-generates SPL queries, correlates evidence across multiple Splunk indexes, and produces investigation reports with confidence scores.
- ⏱️ **Timeline Agent** — reconstructs the complete attack kill chain (Initial Access → Lateral Movement → Exfiltration) mapped to MITRE ATT&CK.
- 📊 **Forecast Agent** — predicts future anomaly windows using the Cisco Deep Time Series Model, separating seasonal patterns from true threats.
- 🛡️ **Response Agent** — generates remediation playbooks with executable SPL queries across immediate, short-term, and long-term actions.

Everything streams to a premium React SOC dashboard via WebSocket — live alert
feed, investigation progress, attack timeline, anomaly forecasts, and response
cards — with a full **demo mode** that runs end-to-end without a live Splunk
instance.

## How we built it

- **Backend** — FastAPI (Python 3.11+) orchestration server. An **Orchestrator
  Agent** coordinates the 5 specialist agents in a streaming pipeline, publishing
  status over WebSocket as each stage completes.
- **AI Layer** — built on Splunk's full AI ecosystem: **Splunk MCP Server** for
  secure, protocol-compliant data access; **Foundation-Sec-1.1-8B-Instruct** as
  the security reasoning engine; **Cisco Deep Time Series Model** for anomaly
  forecasting; **Python SDK AI** for agentic alert actions; and the **AI
  Assistant** for natural-language-to-SPL generation.
- **Connectors** — pluggable clients (`splunk_mcp_client`, `splunk_sdk_client`,
  `hosted_models_client`) abstract live Splunk vs. demo mode behind one interface.
- **Frontend** — React 18 + Vite SOC dashboard with real-time components: alert
  feed, investigation panel, timeline view, anomaly forecast charts, threat map,
  and response actions, all driven by a WebSocket API client.
- **Splunk App** — a packaged Splunk app (`splunk_app/`) with custom alert
  actions and modular inputs built on the Python SDK AI runtime for agentic
  workflows inside Splunk itself.
- **Infrastructure** — one-command `docker-compose up --build` for the full
  stack, with realistic bundled datasets so judges can run it without Splunk.

## Challenges we ran into

- **Coordinating 5 agents into a coherent pipeline** — designing an orchestrator
  that streams partial results without agents blocking or stepping on each other.
- **Demo without a live Splunk instance** — building faithful sample datasets and
  a demo-mode connector layer so the entire pipeline runs end-to-end offline.
- **Real-time streaming UX** — keeping the dashboard responsive with live
  WebSocket updates as each agent emits status, without flooding the client.
- **Security-grade reasoning** — getting the LLM to produce trustworthy,
  MITRE-mapped analysis with evidence and confidence scores rather than vague text.
- **Forecast signal vs. noise** — tuning the time-series model to distinguish
  seasonal patterns from genuine anomalies and surface meaningful risk windows.

## Accomplishments that we're proud of

- A genuinely **autonomous SOC pipeline**: triage → investigate → timeline →
  forecast → respond, end to end.
- **Uses all 5 Splunk AI capabilities** (MCP, Foundation-Sec, Cisco DTSM, Python
  SDK AI, AI Assistant) — not just one.
- **Explainable output** — every investigation ships with evidence, MITRE
  mapping, and confidence scores; every response includes executable SPL.
- A polished, real-time **SOC dashboard** that makes agent activity legible.
- **Zero-friction evaluation** — `docker-compose up` runs the full experience on
  bundled data with no Splunk required.

## What we learned

- **Multi-agent beats monolith for security** — splitting triage, investigation,
  and response into specialists made each step more accurate and debuggable.
- **Context is the product** — analysts don't need more alerts, they need
  correlation, kill-chain narrative, and a recommended action.
- **Demo mode is a feature, not a shortcut** — a faithful offline path made the
  project instantly evaluable and far easier to develop against.
- **Streaming changes the UX** — showing agents "thinking" in real time builds
  trust in the automation far more than a final report alone.

## What's next for SplunkSentinel

- **SOAR integration** — push generated playbooks directly into Splunk SOAR for automated response execution.
- **Multi-tenant support** — isolated agent pipelines for multiple SOC teams.
- **Custom agent training** — fine-tune Foundation-Sec on org-specific threat patterns.
- **Compliance reporting** — auto-generate SOC 2, HIPAA, and PCI-DSS reports.
- **Threat hunting mode** — a proactive agent that hunts hidden threats instead of waiting for alerts.

---

## 🧰 Built With

**Languages**
- `python` (3.11+)
- `javascript` (JSX / ES modules)

**Frontend**
- `react` (18)
- `vite` (5)
- `css` (custom SOC dashboard styling)
- `websocket` (real-time streaming)

**Backend / API**
- `fastapi` (0.115)
- `uvicorn`
- `pydantic` (v2) + `pydantic-settings`
- `httpx`
- `websockets`
- `structlog`

**Splunk AI Ecosystem**
- `splunk-mcp-server` (Model Context Protocol)
- `foundation-sec-1.1-8b-instruct` (security LLM)
- `cisco-deep-time-series-model` (anomaly forecasting)
- `splunk-python-sdk-ai` (`splunk-sdk` — agentic alert actions & modular inputs)
- `splunk-ai-assistant` (natural language → SPL)

**Security Frameworks**
- `mitre-attack` (kill-chain & technique mapping)

**Infrastructure / DevOps**
- `docker`
- `docker-compose`

### Devpost comma-separated tag list (copy-paste ready)
```
python, javascript, react, vite, fastapi, uvicorn, pydantic, websockets, httpx, structlog, splunk, splunk-mcp, foundation-sec, cisco-dtsm, splunk-python-sdk, splunk-ai-assistant, mitre-attack, docker, docker-compose, soc, cybersecurity, multi-agent, llm
```

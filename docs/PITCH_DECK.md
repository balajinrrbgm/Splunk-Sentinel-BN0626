# 🎤 SplunkSentinel — Pitch Deck

> AI-Powered Autonomous SOC Analyst — From Alert Storm to Actionable Intelligence in Seconds

---

## Slide 1 — Title

# 🛡️ SplunkSentinel
### AI-Powered Autonomous SOC Analyst

*"From alert storm to actionable intelligence — in seconds."*

Built on Splunk's complete AI ecosystem.

---

## Slide 2 — The Problem

### SOC teams are drowning

- **4,484 alerts/day** — average for an enterprise SOC *(Palo Alto Networks, 2024)*
- **67% of alerts ignored** — analysts can't keep up
- **197 days** — mean time to detect a breach *(IBM, 2024)*
- **$4.88M** — average cost of a data breach
- **78% of analysts** experience burnout *(Tines, 2024)*

> The alert storm isn't a technology problem — it's an **intelligence problem**.

---

## Slide 3 — The Solution

### Five AI agents. One autonomous SOC analyst.

SplunkSentinel deploys **5 specialized agents** that collaborate to transform
raw Splunk security data into prioritized, investigated, and actionable
intelligence — in real time.

**Human-AI collaboration: agents handle the noise, analysts focus on decisions.**

---

## Slide 4 — How It Works

### The Agent Pipeline

```
🔍 TRIAGE → 🕵️ INVESTIGATE → ⏱️ TIMELINE → 📊 FORECAST → 🛡️ RESPOND
```

| Agent | Job |
|-------|-----|
| 🔍 **Triage** | Score, prioritize & deduplicate alerts (MITRE ATT&CK) |
| 🕵️ **Investigation** | Auto-generate SPL, correlate evidence across indexes |
| ⏱️ **Timeline** | Reconstruct the attack kill chain |
| 📊 **Forecast** | Predict anomaly windows ahead of time |
| 🛡️ **Response** | Generate playbooks with executable SPL |

---

## Slide 5 — Powered by ALL 5 Splunk AI Capabilities

| Capability | How We Use It |
|-----------|---------------|
| **Splunk MCP Server** | Secure, protocol-compliant data access for every query |
| **Foundation-Sec-1.1-8B** | Security reasoning for triage, investigation & response |
| **Cisco Deep Time Series Model** | Anomaly forecasting & risk windows |
| **Python SDK AI** | Custom alert actions & modular inputs in Splunk |
| **AI Assistant** | Natural language → SPL query generation |

> Not one Splunk AI feature — **all five**, working together.

---

## Slide 6 — Live Demo Highlights

| Moment | What You See |
|--------|--------------|
| Triage | Thousands of alerts scored & prioritized in seconds |
| Investigate | SPL auto-generated, evidence correlated, confidence scored |
| Timeline | Full kill chain: Initial Access → Lateral Movement → Exfiltration |
| Forecast | Predicted anomaly windows on a live chart |
| Respond | Ready-to-run remediation playbook with SPL |

All streamed live to a premium React SOC dashboard via WebSocket.

---

## Slide 7 — Architecture

![SplunkSentinel Architecture](diagrams/architecture.png)

- **Data** → Splunk MCP Server → **Orchestrator** → 5 specialist agents
- AI models (Foundation-Sec, Cisco DTSM) wired per-agent
- Results streamed to the dashboard over WebSocket

---

## Slide 8 — Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11+, FastAPI, WebSocket |
| Frontend | React 18, Vite |
| AI | Foundation-Sec-1.1-8B, Cisco DTSM |
| Integration | Splunk MCP Server, Python SDK AI, AI Assistant |
| Frameworks | MITRE ATT&CK |
| Deployment | Docker Compose (one command) |

---

## Slide 9 — Why It Wins

1. **Autonomous, end-to-end** — triage to remediation, no human babysitting required
2. **Uses all 5 Splunk AI capabilities** — deep ecosystem integration
3. **Explainable** — evidence, MITRE mapping & confidence on every output
4. **Zero-friction demo** — `docker-compose up`, no live Splunk needed
5. **Real impact** — collapses 197-day detection into seconds of triage

---

## Slide 10 — What's Next

- **SOAR integration** — automated response execution
- **Multi-tenant** — isolated pipelines per SOC team
- **Custom agent training** — fine-tune on org-specific threats
- **Compliance reporting** — SOC 2, HIPAA, PCI-DSS
- **Threat hunting mode** — proactive, not reactive

---

## Slide 11 — Thank You

# 🛡️ SplunkSentinel
### From Alert Storm to Actionable Intelligence

**5 Agents · All 5 Splunk AI Capabilities · One Autonomous SOC Analyst**

*The future of security operations is autonomous.*

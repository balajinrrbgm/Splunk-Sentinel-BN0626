# 🎬 SplunkSentinel — 3-Minute Demo Video Script

**Total runtime:** ~3:00 · **Format:** screen recording + voiceover · **Tone:** confident, fast-paced

---

## Shot List & Timing

| Time | Scene | On-Screen | Voiceover |
|------|-------|-----------|-----------|
| 0:00–0:15 | **Hook** | Title card → SOC dashboard flooded with alerts | "Every day, security teams face over four thousand alerts. Two out of three get ignored. The average breach takes 197 days to detect. The problem isn't data — it's intelligence." |
| 0:15–0:30 | **Intro** | SplunkSentinel logo + 5 agent icons | "Meet SplunkSentinel — five specialized AI agents that act as an autonomous SOC analyst, turning Splunk's raw alert storm into prioritized, investigated, actionable intelligence in seconds." |
| 0:30–0:50 | **Triage Agent** | Live alert feed scoring & sorting | "It starts with the Triage Agent. Using Splunk's Foundation-Sec security model, it scores thousands of alerts, maps them to MITRE ATT&CK, deduplicates the noise, and surfaces what actually matters — instantly." |
| 0:50–1:15 | **Investigation Agent** | SPL auto-generated, evidence panel fills | "Click a critical alert and the Investigation Agent takes over. It auto-generates SPL queries through Splunk's AI Assistant, correlates evidence across multiple indexes, and produces a full report — with evidence and a confidence score. No manual querying." |
| 1:15–1:40 | **Timeline Agent** | Kill-chain timeline animates | "The Timeline Agent reconstructs the entire attack. Initial access, lateral movement, exfiltration — every stage mapped to the MITRE kill chain, so analysts see the whole story at a glance." |
| 1:40–2:05 | **Forecast Agent** | Anomaly forecast chart with risk window | "Then it looks ahead. Powered by Cisco's Deep Time Series Model, the Forecast Agent predicts the next anomaly windows — separating seasonal patterns from real threats before they hit." |
| 2:05–2:30 | **Response Agent** | Playbook cards with executable SPL | "Finally, the Response Agent writes the playbook — immediate, short-term, and long-term actions, each with executable SPL. From alert to remediation plan, automatically." |
| 2:30–2:45 | **Architecture** | Architecture diagram, MCP highlighted | "Under the hood, everything flows through the Splunk MCP Server for secure access, orchestrated across all five Splunk AI capabilities, and streamed live to the dashboard over WebSocket." |
| 2:45–3:00 | **Close** | Metrics + GitHub URL + tagline | "SplunkSentinel: from alert storm to actionable intelligence in seconds. Five agents. One autonomous SOC analyst. The future of security operations — try it with a single command." |

---

## Voiceover Script (continuous read)

> Every day, security teams face over four thousand alerts. Two out of three get
> ignored. The average breach takes 197 days to detect. The problem isn't data —
> it's intelligence.
>
> Meet SplunkSentinel — five specialized AI agents that act as an autonomous SOC
> analyst, turning Splunk's raw alert storm into prioritized, investigated,
> actionable intelligence in seconds.
>
> It starts with the **Triage Agent**. Using Splunk's Foundation-Sec security
> model, it scores thousands of alerts, maps them to MITRE ATT&CK, deduplicates
> the noise, and surfaces what actually matters — instantly.
>
> Click a critical alert and the **Investigation Agent** takes over. It
> auto-generates SPL queries through Splunk's AI Assistant, correlates evidence
> across multiple indexes, and produces a full report — with evidence and a
> confidence score. No manual querying.
>
> The **Timeline Agent** reconstructs the entire attack. Initial access, lateral
> movement, exfiltration — every stage mapped to the MITRE kill chain, so
> analysts see the whole story at a glance.
>
> Then it looks ahead. Powered by Cisco's Deep Time Series Model, the **Forecast
> Agent** predicts the next anomaly windows — separating seasonal patterns from
> real threats before they hit.
>
> Finally, the **Response Agent** writes the playbook — immediate, short-term,
> and long-term actions, each with executable SPL. From alert to remediation
> plan, automatically.
>
> Under the hood, everything flows through the Splunk MCP Server for secure
> access, orchestrated across all five Splunk AI capabilities, and streamed live
> to the dashboard over WebSocket.
>
> SplunkSentinel: from alert storm to actionable intelligence in seconds. Five
> agents. One autonomous SOC analyst. The future of security operations — try it
> with a single command.

---

## Production Notes

- **Capture demo mode** (`DEMO_MODE=true docker-compose up`) so the pipeline runs end-to-end without a live Splunk instance.
- **Resolution:** 1920×1080, 30fps minimum. Record the dashboard at `http://localhost:5173`.
- **Pacing:** keep each agent segment tight (~20–25s). Use subtle zoom-ins on the active panel.
- **Captions:** burn in agent names as lower-thirds as each one activates.
- **Music:** low-tension electronic bed, ducked under voiceover.
- **End card:** repo URL, MIT license badge, and the tagline "From Alert Storm to Actionable Intelligence."

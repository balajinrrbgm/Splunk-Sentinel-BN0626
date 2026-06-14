import { useState, useEffect } from 'react'
import AlertFeed from './AlertFeed'
import InvestigationPanel from './InvestigationPanel'
import TimelineView from './TimelineView'
import ThreatMap from './ThreatMap'
import AgentStatus from './AgentStatus'
import ResponseActions from './ResponseActions'
import AnomalyForecast from './AnomalyForecast'
import MetricsBar from './MetricsBar'
import { fetchTriagedAlerts, investigateAlert, fetchTimeline, fetchResponseActions, fetchForecast } from '../utils/api'

export default function Dashboard({ health, connected }) {
  const [alerts, setAlerts] = useState([])
  const [selectedAlert, setSelectedAlert] = useState(null)
  const [investigation, setInvestigation] = useState(null)
  const [timeline, setTimeline] = useState(null)
  const [responses, setResponses] = useState(null)
  const [forecast, setForecast] = useState(null)
  const [investigating, setInvestigating] = useState(false)
  const [agentProgress, setAgentProgress] = useState([])

  useEffect(() => {
    loadAlerts()
    loadForecast()
  }, [])

  async function loadAlerts() {
    try {
      const data = await fetchTriagedAlerts(20)
      setAlerts(data.alerts || [])
    } catch {
      // Use demo data on failure
      setAlerts(getDemoAlerts())
    }
  }

  async function loadForecast() {
    try {
      const data = await fetchForecast('network_traffic', 24)
      setForecast(data)
    } catch {
      setForecast(getDemoForecast())
    }
  }

  async function handleInvestigate(alert) {
    setSelectedAlert(alert)
    setInvestigating(true)
    setAgentProgress([])
    setInvestigation(null)
    setTimeline(null)
    setResponses(null)

    // Simulate streaming progress
    const stages = [
      { icon: '🔍', agent: 'Triage Agent', message: 'Analyzing alert severity and threat score...' },
      { icon: '🕵️', agent: 'Investigation Agent', message: 'Correlating events across 5 indexes...' },
      { icon: '⏱️', agent: 'Timeline Agent', message: 'Reconstructing attack kill chain...' },
      { icon: '📊', agent: 'Forecast Agent', message: 'Predicting next 24h anomaly windows...' },
      { icon: '🛡️', agent: 'Response Agent', message: 'Generating remediation playbook...' },
    ]

    for (let i = 0; i < stages.length; i++) {
      await new Promise(r => setTimeout(r, 1200))
      setAgentProgress(prev => [...prev, { ...stages[i], status: 'active' }])
      if (i > 0) {
        setAgentProgress(prev => prev.map((s, idx) => idx === i - 1 ? { ...s, status: 'complete' } : s))
      }
    }

    try {
      const result = await investigateAlert(alert.id)
      setInvestigation(result)

      const tl = await fetchTimeline(alert.id)
      setTimeline(tl)

      const resp = await fetchResponseActions(alert.id)
      setResponses(resp)
    } catch {
      setInvestigation(getDemoInvestigation(alert.id))
      setTimeline(getDemoTimeline())
      setResponses(getDemoResponses())
    }

    setAgentProgress(prev => prev.map(s => ({ ...s, status: 'complete' })))
    setInvestigating(false)
  }

  return (
    <div className="dashboard-wrapper">
      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <span style={{ fontSize: '1.5rem' }}>🛡️</span>
          <h1>SplunkSentinel</h1>
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginLeft: 8 }}>
            AI-Powered Autonomous SOC Analyst
          </span>
        </div>
        <div className="header-status">
          <span className={`status-dot ${connected ? '' : 'disconnected'}`}></span>
          <span>{connected ? 'Connected' : 'Offline'}</span>
          {health?.demo_mode && (
            <span style={{ marginLeft: 12, padding: '2px 8px', background: 'rgba(168,85,247,0.15)', color: 'var(--accent-purple)', borderRadius: 4, fontSize: '0.7rem' }}>
              DEMO MODE
            </span>
          )}
        </div>
      </header>

      {/* Metrics Bar */}
      <MetricsBar alerts={alerts} health={health} />

      {/* Main Grid */}
      <div className="dashboard-grid">
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, overflow: 'hidden' }}>
          <div className="card" style={{ flex: 2, overflow: 'hidden' }}>
            <AlertFeed alerts={alerts} onInvestigate={handleInvestigate} selectedId={selectedAlert?.id} />
          </div>
          <div className="card" style={{ flex: 1 }}>
            <AgentStatus health={health} progress={agentProgress} />
          </div>
        </div>

        {/* Center Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, overflow: 'hidden' }}>
          <div className="card" style={{ flex: 1, overflow: 'hidden' }}>
            <InvestigationPanel
              alert={selectedAlert}
              investigation={investigation}
              progress={agentProgress}
              investigating={investigating}
            />
          </div>
          <div className="card" style={{ flex: 1, overflow: 'hidden' }}>
            <TimelineView timeline={timeline} />
          </div>
        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, overflow: 'hidden' }}>
          <div className="card" style={{ flex: 1 }}>
            <AnomalyForecast forecast={forecast} />
          </div>
          <div className="card" style={{ flex: 1, overflow: 'hidden' }}>
            <ResponseActions responses={responses} />
          </div>
        </div>
      </div>
    </div>
  )
}

// Demo fallback data
function getDemoAlerts() {
  return [
    { id: 'ALT-2024-001', title: 'Brute Force Attack - Multiple Failed Logins', severity: 'Critical', threat_score: 92, source_ip: '185.220.101.42', dest_ip: '10.0.1.50', user: 'admin', host: 'server-prod-01', mitre_techniques: [{ id: 'T1110', name: 'Brute Force' }], timestamp: '2024-12-01T08:15:30Z' },
    { id: 'ALT-2024-002', title: 'SQL Injection Attempt on Web App', severity: 'High', threat_score: 78, source_ip: '91.198.174.20', dest_ip: '10.0.2.10', user: 'anonymous', host: 'web-frontend-03', mitre_techniques: [{ id: 'T1190', name: 'Exploit Public-Facing App' }], timestamp: '2024-12-01T08:22:15Z' },
    { id: 'ALT-2024-003', title: 'Lateral Movement - RDP to Multiple Hosts', severity: 'Critical', threat_score: 95, source_ip: '10.0.1.50', dest_ip: '10.0.3.25', user: 'svc_backup', host: 'dc-primary', mitre_techniques: [{ id: 'T1021', name: 'Remote Services' }], timestamp: '2024-12-01T08:45:00Z' },
    { id: 'ALT-2024-004', title: 'Data Exfiltration - Large Outbound Transfer', severity: 'Critical', threat_score: 97, source_ip: '10.0.4.15', dest_ip: '203.0.113.50', user: 'jsmith', host: 'workstation-dev-07', mitre_techniques: [{ id: 'T1048', name: 'Exfiltration Over Alt Protocol' }], timestamp: '2024-12-01T09:10:22Z' },
    { id: 'ALT-2024-005', title: 'Privilege Escalation - Unauthorized Admin', severity: 'High', threat_score: 82, source_ip: '10.0.1.22', dest_ip: '10.0.1.1', user: 'temp_contractor', host: 'server-prod-02', mitre_techniques: [{ id: 'T1068', name: 'Exploitation for Privilege Escalation' }], timestamp: '2024-12-01T09:30:45Z' },
    { id: 'ALT-2024-006', title: 'Suspicious DNS - Possible Tunneling', severity: 'High', threat_score: 74, source_ip: '10.0.5.33', dest_ip: '8.8.8.8', user: 'N/A', host: 'workstation-mkt-12', mitre_techniques: [{ id: 'T1071', name: 'Application Layer Protocol' }], timestamp: '2024-12-01T09:45:10Z' },
    { id: 'ALT-2024-007', title: 'Internal Port Scan Detected', severity: 'Medium', threat_score: 55, source_ip: '10.0.1.50', dest_ip: '10.0.0.0/16', user: 'N/A', host: 'server-prod-01', mitre_techniques: [{ id: 'T1046', name: 'Network Service Discovery' }], timestamp: '2024-12-01T08:50:00Z' },
    { id: 'ALT-2024-008', title: 'Cobalt Strike Beacon Communication', severity: 'Critical', threat_score: 99, source_ip: '10.0.3.25', dest_ip: '198.51.100.77', user: 'SYSTEM', host: 'dc-primary', mitre_techniques: [{ id: 'T1071', name: 'Application Layer Protocol' }], timestamp: '2024-12-01T09:55:30Z' },
  ]
}

function getDemoInvestigation(alertId) {
  return { alert_id: alertId, state: 'complete', results: { investigation: { findings: { summary: 'High-confidence brute force attack with credential compromise and lateral movement detected.', confidence_score: 92, attack_pattern: 'Credential Stuffing → Initial Access → Privilege Escalation → Lateral Movement', affected_assets: ['server-prod-01', 'dc-primary'], mitre_techniques: [{ id: 'T1110', name: 'Brute Force' }, { id: 'T1078', name: 'Valid Accounts' }, { id: 'T1021', name: 'Remote Services' }] } } } }
}

function getDemoTimeline() {
  return { timeline: [
    { timestamp: '2024-12-01T07:00:00Z', stage: 'Reconnaissance', event: 'Port scan from 185.220.101.42', severity: 'Low' },
    { timestamp: '2024-12-01T07:15:00Z', stage: 'Initial Access', event: 'Brute force attack initiated (847 attempts)', severity: 'High' },
    { timestamp: '2024-12-01T08:00:00Z', stage: 'Initial Access', event: 'Successful login — admin compromised', severity: 'Critical' },
    { timestamp: '2024-12-01T08:05:00Z', stage: 'Discovery', event: 'Internal network enumeration', severity: 'Medium' },
    { timestamp: '2024-12-01T08:20:00Z', stage: 'Privilege Escalation', event: 'Service account credentials harvested', severity: 'Critical' },
    { timestamp: '2024-12-01T08:45:00Z', stage: 'Lateral Movement', event: 'RDP to domain controller', severity: 'Critical' },
    { timestamp: '2024-12-01T09:00:00Z', stage: 'Collection', event: 'NTDS.dit database accessed', severity: 'Critical' },
    { timestamp: '2024-12-01T09:10:00Z', stage: 'Exfiltration', event: '2.3GB transferred to external IP', severity: 'Critical' },
  ] }
}

function getDemoResponses() {
  return { playbook: { immediate_actions: [
    { action: 'Block attacker IP at firewall', priority: 1, spl: '| makeresults | eval action="block", ip="185.220.101.42" | sendalert firewall_block' },
    { action: 'Disable compromised admin account', priority: 2, spl: '| makeresults | eval action="disable_account", user="admin" | sendalert ad_account_action' },
    { action: 'Isolate affected hosts', priority: 3, spl: '| makeresults | eval action="isolate", hosts="server-prod-01,dc-primary" | sendalert network_isolate' },
  ], short_term_actions: [
    { action: 'Rotate all credentials on affected systems', priority: 1, timeframe: 'Within 4 hours' },
    { action: 'Block Tor exit nodes at perimeter', priority: 2, timeframe: 'Within 4 hours' },
  ], long_term_actions: [
    { action: 'Implement MFA for all admin accounts', priority: 1, timeframe: 'Within 1 week' },
    { action: 'Deploy network segmentation', priority: 2, timeframe: 'Within 2 weeks' },
  ] } }
}

function getDemoForecast() {
  const now = Date.now()
  const historical = Array.from({ length: 48 }, (_, i) => ({
    timestamp: new Date(now - (48 - i) * 3600000).toISOString(),
    value: 1000 + 500 * Math.sin(2 * Math.PI * i / 24) + (Math.random() - 0.5) * 200,
    type: 'historical',
  }))
  const forecast = Array.from({ length: 24 }, (_, i) => {
    const isAnomaly = i === 3 || i === 4 || i === 14
    const base = 1000 + 500 * Math.sin(2 * Math.PI * (48 + i) / 24)
    const value = isAnomaly ? base * 2.5 : base + (Math.random() - 0.5) * 100
    return {
      timestamp: new Date(now + i * 3600000).toISOString(),
      value,
      upper_bound: value + 50 + i * 10,
      lower_bound: Math.max(0, value - 50 - i * 10),
      is_anomaly: isAnomaly,
      anomaly_score: isAnomaly ? 0.92 : Math.random() * 0.3,
      type: 'forecast',
    }
  })
  return { metric: 'network_traffic', historical, forecast, anomalies_predicted: 3, model: 'Cisco Deep Time Series Model' }
}

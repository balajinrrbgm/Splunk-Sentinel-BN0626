export default function MetricsBar({ alerts, health }) {
  const criticalCount = alerts.filter(a => a.severity === 'Critical').length
  const totalAlerts = alerts.length
  const agentUptime = health?.agents?.orchestrator === 'active' ? '99.7%' : '—'

  return (
    <div className="metrics-bar">
      <div className="metric-item">
        <span className="metric-value critical">{criticalCount}</span>
        <span className="metric-label">Active Threats</span>
      </div>
      <div className="metric-item">
        <span className="metric-value warning">{totalAlerts}</span>
        <span className="metric-label">Alerts Triaged</span>
      </div>
      <div className="metric-item">
        <span className="metric-value cyan">4.2m</span>
        <span className="metric-label">MTTD</span>
      </div>
      <div className="metric-item">
        <span className="metric-value cyan">12.8m</span>
        <span className="metric-label">MTTR</span>
      </div>
      <div className="metric-item">
        <span className="metric-value success">{agentUptime}</span>
        <span className="metric-label">Agent Uptime</span>
      </div>
      <div className="metric-item">
        <span className="metric-value success">5/5</span>
        <span className="metric-label">Agents Online</span>
      </div>
      <div className="metric-item">
        <span className="metric-value" style={{ color: 'var(--accent-purple)' }}>92%</span>
        <span className="metric-label">Confidence</span>
      </div>
    </div>
  )
}

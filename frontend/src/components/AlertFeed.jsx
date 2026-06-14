export default function AlertFeed({ alerts, onInvestigate, selectedId }) {
  return (
    <>
      <div className="panel-header">
        <span className="panel-title">🚨 Alert Feed</span>
        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{alerts.length} alerts</span>
      </div>
      <div className="alert-feed">
        {alerts.map(alert => (
          <div
            key={alert.id}
            className={`alert-item ${alert.severity?.toLowerCase()}`}
            style={selectedId === alert.id ? { background: 'var(--glass)', borderColor: 'var(--accent-cyan)' } : {}}
          >
            <span className={`severity-dot ${alert.severity?.toLowerCase()}`}></span>
            <div className="alert-content">
              <div className="alert-title">{alert.title}</div>
              <div className="alert-meta">
                <span className="alert-tag">{alert.source_ip}</span>
                <span className="alert-tag">{alert.user}</span>
                {alert.mitre_techniques?.slice(0, 2).map(t => (
                  <span key={t.id} className="alert-tag mitre">{t.id}</span>
                ))}
              </div>
              <div className="threat-score-bar">
                <div
                  className="threat-score-fill"
                  style={{
                    width: `${alert.threat_score}%`,
                    background: alert.threat_score > 80 ? 'var(--critical)'
                      : alert.threat_score > 60 ? 'var(--warning)'
                      : 'var(--accent-cyan)',
                  }}
                />
              </div>
            </div>
            <button className="btn-investigate" onClick={() => onInvestigate(alert)}>
              Investigate
            </button>
          </div>
        ))}
        {alerts.length === 0 && (
          <div style={{ padding: 24, textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            No alerts loaded. Connect to backend or enable demo mode.
          </div>
        )}
      </div>
    </>
  )
}

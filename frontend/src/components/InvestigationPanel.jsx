export default function InvestigationPanel({ alert, investigation, progress, investigating }) {
  if (!alert) {
    return (
      <>
        <div className="panel-header">
          <span className="panel-title">🕵️ Investigation Panel</span>
        </div>
        <div className="investigation-panel" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
          <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
            <div style={{ fontSize: '2rem', marginBottom: 12 }}>🔍</div>
            <div style={{ fontSize: '0.85rem' }}>Select an alert to begin investigation</div>
            <div style={{ fontSize: '0.7rem', marginTop: 4 }}>AI agents will analyze, correlate, and report findings</div>
          </div>
        </div>
      </>
    )
  }

  const findings = investigation?.results?.investigation?.findings

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">🕵️ Investigating: {alert.id}</span>
        {investigating && <span className="stage-status active">LIVE</span>}
        {!investigating && investigation && <span className="stage-status complete">COMPLETE</span>}
      </div>
      <div className="investigation-panel">
        {/* Agent Progress */}
        {progress.map((stage, i) => (
          <div key={i} className="investigation-stage">
            <span className="stage-icon">{stage.icon}</span>
            <div className="stage-content">
              <div className="stage-title">{stage.agent}</div>
              <div className="stage-description">{stage.message}</div>
            </div>
            <span className={`stage-status ${stage.status}`}>
              {stage.status === 'active' ? '⏳' : '✅'}
            </span>
          </div>
        ))}

        {/* Findings Summary */}
        {findings && (
          <div style={{ marginTop: 16, padding: 16, background: 'var(--glass)', borderRadius: 'var(--radius-sm)', border: '1px solid var(--glass-border)' }}>
            <div style={{ fontSize: '0.8rem', fontWeight: 600, marginBottom: 8, color: 'var(--accent-cyan)' }}>
              📋 Findings (Confidence: {findings.confidence_score}%)
            </div>
            <div style={{ fontSize: '0.78rem', lineHeight: 1.5, color: 'var(--text-primary)', marginBottom: 12 }}>
              {findings.summary}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginBottom: 8 }}>
              <strong>Attack Pattern:</strong> {findings.attack_pattern}
            </div>
            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
              {findings.mitre_techniques?.map(t => (
                <span key={t.id} className="alert-tag mitre">{t.id}: {t.name}</span>
              ))}
            </div>
            {findings.affected_assets && (
              <div style={{ fontSize: '0.72rem', color: 'var(--text-secondary)', marginTop: 8 }}>
                <strong>Affected Assets:</strong> {findings.affected_assets.join(', ')}
              </div>
            )}
          </div>
        )}
      </div>
    </>
  )
}

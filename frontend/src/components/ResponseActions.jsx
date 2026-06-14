export default function ResponseActions({ responses }) {
  const playbook = responses?.playbook

  if (!playbook) {
    return (
      <>
        <div className="panel-header">
          <span className="panel-title">🛡️ Response Actions</span>
        </div>
        <div className="response-actions" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>🛡️</div>
            Response playbook will appear after investigation
          </div>
        </div>
      </>
    )
  }

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">🛡️ Response Actions</span>
      </div>
      <div className="response-actions">
        {/* Immediate Actions */}
        {playbook.immediate_actions?.length > 0 && (
          <div className="response-category">
            <div className="response-category-title immediate">⚡ Immediate</div>
            {playbook.immediate_actions.map((action, i) => (
              <div key={i} className="response-item">
                <div className="response-item-title">{action.action}</div>
                {action.spl && <div className="response-item-spl">{action.spl}</div>}
              </div>
            ))}
          </div>
        )}

        {/* Short-term Actions */}
        {playbook.short_term_actions?.length > 0 && (
          <div className="response-category">
            <div className="response-category-title short-term">📋 Short-term</div>
            {playbook.short_term_actions.map((action, i) => (
              <div key={i} className="response-item">
                <div className="response-item-title">{action.action}</div>
                {action.timeframe && (
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    {action.timeframe}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}

        {/* Long-term Actions */}
        {playbook.long_term_actions?.length > 0 && (
          <div className="response-category">
            <div className="response-category-title long-term">🗓️ Long-term</div>
            {playbook.long_term_actions.map((action, i) => (
              <div key={i} className="response-item">
                <div className="response-item-title">{action.action}</div>
                {action.timeframe && (
                  <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 4 }}>
                    {action.timeframe}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  )
}

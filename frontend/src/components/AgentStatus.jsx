export default function AgentStatus({ health, progress }) {
  const agents = [
    { icon: '🎯', name: 'Orchestrator', status: 'active' },
    { icon: '🔍', name: 'Triage Agent', status: 'active' },
    { icon: '🕵️', name: 'Investigation Agent', status: 'active' },
    { icon: '⏱️', name: 'Timeline Agent', status: 'active' },
    { icon: '📊', name: 'Forecast Agent', status: 'active' },
    { icon: '🛡️', name: 'Response Agent', status: 'active' },
  ]

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">🤖 Agent Status</span>
      </div>
      <div className="agent-status-list">
        {agents.map((agent, i) => {
          const progressItem = progress.find(p => p.agent === agent.name)
          const displayStatus = progressItem?.status === 'active' ? 'working'
            : progressItem?.status === 'complete' ? 'done'
            : 'idle'

          return (
            <div key={i} className="agent-status-item">
              <span className="agent-name">
                <span>{agent.icon}</span>
                <span>{agent.name}</span>
              </span>
              <span className="agent-badge" style={
                displayStatus === 'working' ? { background: 'rgba(0,212,255,0.15)', color: 'var(--accent-cyan)' }
                : displayStatus === 'done' ? { background: 'rgba(46,204,113,0.15)', color: 'var(--success)' }
                : {}
              }>
                {displayStatus === 'working' ? '⚡ Active' : displayStatus === 'done' ? '✅ Done' : '● Online'}
              </span>
            </div>
          )
        })}
      </div>
    </>
  )
}

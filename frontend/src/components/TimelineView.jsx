export default function TimelineView({ timeline }) {
  const events = timeline?.timeline || []

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">⏱️ Attack Timeline</span>
        {events.length > 0 && (
          <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
            {events.length} events | {timeline?.duration || ''}
          </span>
        )}
      </div>
      <div className="timeline-container">
        {events.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 32, color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            <div style={{ fontSize: '1.5rem', marginBottom: 8 }}>⏱️</div>
            Timeline will appear after investigation
          </div>
        ) : (
          <div className="timeline">
            {events.map((event, i) => (
              <div key={i} className={`timeline-event ${event.severity?.toLowerCase()}`}>
                <div className="timeline-time">
                  {new Date(event.timestamp).toLocaleTimeString()} 
                </div>
                <span className="timeline-stage-badge">{event.stage}</span>
                <div className="timeline-event-title">{event.event}</div>
                {event.details && (
                  <div className="timeline-details">{event.details}</div>
                )}
                {(event.source_ip || event.dest_ip) && (
                  <div style={{ display: 'flex', gap: 6, marginTop: 4 }}>
                    {event.source_ip && <span className="alert-tag">{event.source_ip}</span>}
                    {event.dest_ip && <span className="alert-tag">→ {event.dest_ip}</span>}
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

export default function AnomalyForecast({ forecast }) {
  if (!forecast) {
    return (
      <>
        <div className="panel-header">
          <span className="panel-title">📊 Anomaly Forecast</span>
        </div>
        <div className="forecast-container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '80%' }}>
          <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.8rem' }}>
            Loading forecast data...
          </div>
        </div>
      </>
    )
  }

  const historical = forecast.historical || []
  const forecastData = forecast.forecast || []
  const allData = [...historical, ...forecastData]

  // Calculate SVG chart dimensions
  const width = 280
  const height = 140
  const padding = { top: 10, right: 10, bottom: 20, left: 30 }
  const chartW = width - padding.left - padding.right
  const chartH = height - padding.top - padding.bottom

  // Normalize values for SVG
  const values = allData.map(d => d.value)
  const maxVal = Math.max(...values) * 1.1
  const minVal = Math.min(...values) * 0.9

  const scaleX = (i) => padding.left + (i / (allData.length - 1)) * chartW
  const scaleY = (v) => padding.top + chartH - ((v - minVal) / (maxVal - minVal)) * chartH

  // Build path strings
  const historicalPath = historical.map((d, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i)} ${scaleY(d.value)}`).join(' ')
  const forecastStart = historical.length
  const forecastPath = forecastData.map((d, i) => {
    const idx = forecastStart + i
    return `${i === 0 ? 'M' : 'L'} ${scaleX(idx)} ${scaleY(d.value)}`
  }).join(' ')

  // Anomaly markers
  const anomalies = forecastData
    .map((d, i) => ({ ...d, idx: forecastStart + i }))
    .filter(d => d.is_anomaly)

  return (
    <>
      <div className="panel-header">
        <span className="panel-title">📊 Anomaly Forecast</span>
        <span style={{ fontSize: '0.65rem', color: 'var(--accent-purple)' }}>
          {forecast.model || 'Cisco DTSM'}
        </span>
      </div>
      <div className="forecast-container">
        <div className="chart-area">
          <svg viewBox={`0 0 ${width} ${height}`} className="chart-svg" preserveAspectRatio="none">
            {/* Historical line */}
            <path d={historicalPath} className="chart-line historical" vectorEffect="non-scaling-stroke" />
            {/* Forecast line */}
            <path d={forecastPath} className="chart-line forecast" vectorEffect="non-scaling-stroke" />
            {/* Divider line */}
            <line
              x1={scaleX(forecastStart)}
              y1={padding.top}
              x2={scaleX(forecastStart)}
              y2={padding.top + chartH}
              stroke="var(--glass-border)"
              strokeDasharray="3 3"
              strokeWidth="1"
            />
            {/* Anomaly dots */}
            {anomalies.map((a, i) => (
              <circle
                key={i}
                cx={scaleX(a.idx)}
                cy={scaleY(a.value)}
                r="4"
                className="chart-anomaly"
              />
            ))}
            {/* Now label */}
            <text x={scaleX(forecastStart)} y={height - 4} fill="var(--text-muted)" fontSize="7" textAnchor="middle">
              NOW
            </text>
          </svg>
        </div>

        <div className="forecast-legend">
          <div className="legend-item">
            <span className="legend-dot" style={{ background: 'var(--accent-cyan)' }}></span>
            <span>Historical</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: 'var(--accent-purple)' }}></span>
            <span>Forecast</span>
          </div>
          <div className="legend-item">
            <span className="legend-dot" style={{ background: 'var(--critical)' }}></span>
            <span>Anomaly ({forecast.anomalies_predicted || anomalies.length})</span>
          </div>
        </div>

        {anomalies.length > 0 && (
          <div style={{ marginTop: 12, padding: 8, background: 'rgba(255,71,87,0.08)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(255,71,87,0.2)' }}>
            <div style={{ fontSize: '0.7rem', color: 'var(--critical)', fontWeight: 500 }}>
              ⚠️ {anomalies.length} anomalies predicted in next 24h
            </div>
            <div style={{ fontSize: '0.65rem', color: 'var(--text-secondary)', marginTop: 4 }}>
              Peak anomaly score: {Math.max(...anomalies.map(a => a.anomaly_score)).toFixed(2)}
            </div>
          </div>
        )}
      </div>
    </>
  )
}

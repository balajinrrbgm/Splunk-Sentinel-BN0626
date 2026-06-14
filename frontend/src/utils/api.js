const API_BASE = '/api'
const WS_BASE = `ws://${window.location.host}`

export async function fetchHealth() {
  const res = await fetch(`${API_BASE}/health`)
  return res.json()
}

export async function fetchTriagedAlerts(limit = 50) {
  const res = await fetch(`${API_BASE}/alerts/triage?limit=${limit}`)
  return res.json()
}

export async function investigateAlert(alertId, context = '', depth = 'full') {
  const res = await fetch(`${API_BASE}/investigate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ alert_id: alertId, context, depth }),
  })
  return res.json()
}

export async function fetchForecast(metric = 'network_traffic', hours = 24) {
  const res = await fetch(`${API_BASE}/forecast?metric=${metric}&hours=${hours}`)
  return res.json()
}

export async function fetchTimeline(alertId) {
  const res = await fetch(`${API_BASE}/timeline/${alertId}`)
  return res.json()
}

export async function fetchResponseActions(alertId) {
  const res = await fetch(`${API_BASE}/response/${alertId}`, { method: 'POST' })
  return res.json()
}

export async function fetchExecutiveReport() {
  const res = await fetch(`${API_BASE}/report/executive`)
  return res.json()
}

export function connectAlertWebSocket(onMessage) {
  const ws = new WebSocket(`${WS_BASE}/ws/alerts`)
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }
  ws.onerror = () => {}
  ws.onclose = () => {
    setTimeout(() => connectAlertWebSocket(onMessage), 5000)
  }
  return ws
}

export function connectInvestigationWebSocket(alertId, onMessage) {
  const ws = new WebSocket(`${WS_BASE}/ws/investigation/${alertId}`)
  ws.onmessage = (event) => {
    const data = JSON.parse(event.data)
    onMessage(data)
  }
  ws.onerror = () => {}
  return ws
}

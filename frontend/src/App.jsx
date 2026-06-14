import { useState, useEffect } from 'react'
import Dashboard from './components/Dashboard'

function App() {
  const [health, setHealth] = useState(null)
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await fetch('/api/health')
        const data = await res.json()
        setHealth(data)
        setConnected(true)
      } catch {
        setConnected(false)
      }
    }
    checkHealth()
    const interval = setInterval(checkHealth, 10000)
    return () => clearInterval(interval)
  }, [])

  return <Dashboard health={health} connected={connected} />
}

export default App

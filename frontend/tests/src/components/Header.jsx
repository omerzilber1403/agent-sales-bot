import React, { useState, useEffect } from 'react'

const Header = () => {
  const [serverStatus, setServerStatus] = useState('checking')

  useEffect(() => {
    checkServerStatus()
    const interval = setInterval(checkServerStatus, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const checkServerStatus = async () => {
    try {
      const response = await fetch('http://localhost:8080/health')
      if (response.ok) {
        setServerStatus('online')
      } else {
        setServerStatus('offline')
      }
    } catch (error) {
      setServerStatus('offline')
    }
  }

  const getStatusText = () => {
    switch (serverStatus) {
      case 'online':
        return 'שרת פעיל'
      case 'offline':
        return 'שרת לא פעיל'
      default:
        return 'בודק חיבור...'
    }
  }

  const getStatusColor = () => {
    switch (serverStatus) {
      case 'online':
        return '#48bb78'
      case 'offline':
        return '#f56565'
      default:
        return '#ed8936'
    }
  }

  return (
    <header className="header">
      <div className="header-content">
        <div className="logo">
          <div className="logo-icon">🤖</div>
          <div className="logo-text">
            <h1>AGENT Dev Console</h1>
            <p>ממשק פיתוח לצ'אטבוט המכירות החכם</p>
          </div>
        </div>
        
        <div className="status-indicator">
          <div 
            className="status-dot" 
            style={{ backgroundColor: getStatusColor() }}
          ></div>
          <span>{getStatusText()}</span>
        </div>
      </div>
    </header>
  )
}

export default Header

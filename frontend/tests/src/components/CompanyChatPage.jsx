import React, { useState, useEffect } from 'react'
import CompanySelector from './CompanySelector'
import CustomerProfile from './CustomerProfile'
import ChatInterface from './ChatInterface'
import StatsPanel from './StatsPanel'
import CreateCustomerModal from './CreateCustomerModal'

const CompanyChatPage = ({ selectedCompany, onBackToSelection }) => {
  const [selectedCustomer, setSelectedCustomer] = useState(null)
  const [currentSession, setCurrentSession] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [stats, setStats] = useState({
    totalMessages: 0,
    handoffs: 0,
    conversations: 0
  })
  const [serverStatus, setServerStatus] = useState('checking')

  useEffect(() => {
    loadStats()
    checkServerStatus()
    const interval = setInterval(checkServerStatus, 30000)
    return () => clearInterval(interval)
  }, [])

  // Load existing session when customer is selected
  useEffect(() => {
    if (selectedCustomer) {
      const existingSession = localStorage.getItem(`session_${selectedCustomer.id}`)
      if (existingSession) {
        setCurrentSession(existingSession)
      }
    }
  }, [selectedCustomer])

  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8080/api/v1/coach/stats')
      if (response.ok) {
        const data = await response.json()
        setStats(data)
      }
    } catch (error) {
      console.error('Error loading stats:', error)
    }
  }

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

  const handleCustomerSelect = (customer) => {
    setSelectedCustomer(customer)
    // Try to get existing session for this customer
    const existingSession = localStorage.getItem(`session_${customer.id}`)
    if (existingSession) {
      setCurrentSession(existingSession)
    } else {
      setCurrentSession(null)
    }
  }

  const handleStartConversation = async () => {
    if (!selectedCompany || !selectedCustomer) {
      alert('בחר חברה ולקוח תחילה')
      return
    }

    try {
      const response = await fetch('http://localhost:8080/api/v1/dev/conversations', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: selectedCompany.id,
          user_id: selectedCustomer.id,
          channel: 'dev'
        })
      })

      if (response.ok) {
        const data = await response.json()
        setCurrentSession(data.session_id)
        // Save session to localStorage for this customer
        localStorage.setItem(`session_${selectedCustomer.id}`, data.session_id)
        console.log('New conversation started:', data)
      } else {
        alert('שגיאה ביצירת שיחה חדשה')
      }
    } catch (error) {
      console.error('Error starting conversation:', error)
      alert('שגיאה ביצירת שיחה חדשה')
    }
  }

  const handleCreateCustomer = () => {
    if (!selectedCompany) {
      alert('בחר חברה תחילה')
      return
    }
    setShowCreateModal(true)
  }

  const handleCustomerCreated = (newCustomer) => {
    setSelectedCustomer(newCustomer)
    setShowCreateModal(false)
    setTimeout(() => {
      handleStartConversation()
    }, 500)
  }

  return (
    <div className="company-chat-page">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <button className="back-button" onClick={onBackToSelection}>
              <span>←</span>
            </button>
            <div className="logo-icon">🤖</div>
            <div className="logo-text">
              <h1>{selectedCompany?.name || 'AGENT Dev Console'}</h1>
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

      {/* Main Content */}
      <div className="app-container">
        <div className="sidebar">
          <CompanySelector 
            selectedCompany={selectedCompany}
            onCustomerSelect={handleCustomerSelect}
            selectedCustomer={selectedCustomer}
            onStartConversation={handleStartConversation}
            onCreateCustomer={handleCreateCustomer}
          />
          
          {selectedCustomer && (
            <CustomerProfile customer={selectedCustomer} />
          )}
        </div>

        <div className="main-content">
          <ChatInterface 
            company={selectedCompany}
            customer={selectedCustomer}
            sessionId={currentSession}
            onStatsUpdate={loadStats}
          />
          
          <StatsPanel stats={stats} />
        </div>
      </div>

      {showCreateModal && (
        <CreateCustomerModal
          company={selectedCompany}
          onClose={() => setShowCreateModal(false)}
          onCustomerCreated={handleCustomerCreated}
        />
      )}
    </div>
  )
}

export default CompanyChatPage

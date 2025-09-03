import React, { useState, useEffect } from 'react'
import CreateCompanyModal from './CreateCompanyModal'

const CompanySelectionPage = ({ onCompanySelect }) => {
  const [companies, setCompanies] = useState([])
  const [loading, setLoading] = useState(true)
  const [serverStatus, setServerStatus] = useState('checking')
  const [showCreateModal, setShowCreateModal] = useState(false)

  useEffect(() => {
    loadCompanies()
    checkServerStatus()
    const interval = setInterval(checkServerStatus, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const loadCompanies = async () => {
    setLoading(true)
    try {
      console.log('Loading companies...')
      const response = await fetch('http://localhost:8080/api/v1/admin/companies')
      console.log('Response status:', response.status)
      if (response.ok) {
        const data = await response.json()
        console.log('Companies loaded:', data)
        setCompanies(data)
      } else {
        console.error('Response not ok:', response.status, response.statusText)
      }
    } catch (error) {
      console.error('Error loading companies:', error)
    } finally {
      setLoading(false)
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

  const handleCompanySelect = (company) => {
    onCompanySelect(company)
  }

  const handleCompanyCreated = (newCompany) => {
    setCompanies(prev => [...prev, newCompany])
  }

  return (
    <div className="company-selection-page">
      {/* Header */}
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

      {/* Main Content */}
      <div className="selection-container">
        <div className="selection-card">
          <div className="selection-header">
            <h2>
              <span className="selection-icon">🏢</span>
              בחר חברה
            </h2>
            <p>בחר חברה כדי להתחיל לעבוד עם הלקוחות שלה</p>
            <button 
              className="btn btn-primary create-company-btn"
              onClick={() => setShowCreateModal(true)}
            >
              <span>➕</span>
              צור חברה חדשה
            </button>
          </div>

          {loading ? (
            <div className="loading">
              <div className="spinner"></div>
              טוען חברות...
            </div>
          ) : (
            <div className="companies-grid">
              {companies.length > 0 ? (
                companies.map(company => (
                  <div 
                    key={company.id} 
                    className="company-card"
                    onClick={() => handleCompanySelect(company)}
                  >
                    <div className="company-icon">🏢</div>
                    <div className="company-info">
                      <h3>{company.name}</h3>
                      <p>{company.domain || 'ללא דומיין'}</p>
                      <div className="company-status">
                        <span className={`status-badge ${company.is_active ? 'active' : 'inactive'}`}>
                          {company.is_active ? 'פעיל' : 'לא פעיל'}
                        </span>
                      </div>
                    </div>
                    <div className="company-arrow">→</div>
                  </div>
                ))
              ) : (
                <div className="no-companies">
                  <div className="no-companies-icon">📭</div>
                  <h3>אין חברות זמינות</h3>
                  <p>צור חברה חדשה כדי להתחיל</p>
                  <p style={{fontSize: '0.8rem', color: '#999'}}>Debug: companies.length = {companies.length}</p>
                </div>
              )}
            </div>
          )}


        </div>
      </div>

      {/* Create Company Modal */}
      <CreateCompanyModal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        onCompanyCreated={handleCompanyCreated}
      />
    </div>
  )
}

export default CompanySelectionPage

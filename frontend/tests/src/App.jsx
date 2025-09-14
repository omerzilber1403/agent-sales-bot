import React, { useState } from 'react'
import CompanySelectionPage from './components/CompanySelectionPage'
import CompanyChatPage from './components/CompanyChatPage'
import DemoInterface from './components/DemoInterface'

// Import CSS
import './App.css'

function App() {
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [currentPage, setCurrentPage] = useState('selection') // 'selection', 'chat', or 'demo'
  const [stats, setStats] = useState({})

  const handleCompanySelect = (company) => {
    setSelectedCompany(company)
    setCurrentPage('chat')
  }

  const handleBackToSelection = () => {
    setSelectedCompany(null)
    setCurrentPage('selection')
  }

  const handleDemoMode = (company) => {
    setSelectedCompany(company)
    setCurrentPage('demo')
  }

  const handleStatsUpdate = (newStats) => {
    setStats(prev => ({ ...prev, ...newStats }))
  }

  return (
    <div className="app">
      {currentPage === 'selection' ? (
        <CompanySelectionPage 
          onCompanySelect={handleCompanySelect}
          onDemoMode={handleDemoMode}
        />
      ) : currentPage === 'demo' ? (
        <DemoInterface 
          company={selectedCompany}
          onStatsUpdate={handleStatsUpdate}
        />
      ) : (
        <CompanyChatPage 
          selectedCompany={selectedCompany}
          onBackToSelection={handleBackToSelection}
        />
      )}
    </div>
  )
}

export default App
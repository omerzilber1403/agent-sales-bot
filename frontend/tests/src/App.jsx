import React, { useState } from 'react'
import CompanySelectionPage from './components/CompanySelectionPage'
import CompanyChatPage from './components/CompanyChatPage'

// Import CSS
import './App.css'

function App() {
  const [selectedCompany, setSelectedCompany] = useState(null)
  const [currentPage, setCurrentPage] = useState('selection') // 'selection' or 'chat'

  const handleCompanySelect = (company) => {
    setSelectedCompany(company)
    setCurrentPage('chat')
  }

  const handleBackToSelection = () => {
    setSelectedCompany(null)
    setCurrentPage('selection')
  }

  return (
    <div className="app">
      {currentPage === 'selection' ? (
        <CompanySelectionPage onCompanySelect={handleCompanySelect} />
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
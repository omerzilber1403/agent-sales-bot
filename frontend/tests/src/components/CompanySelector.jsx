import React, { useState, useEffect } from 'react'

const CompanySelector = ({ 
  selectedCompany,
  onCustomerSelect, 
  selectedCustomer,
  onStartConversation,
  onCreateCustomer 
}) => {
  const [customers, setCustomers] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (selectedCompany) {
      loadCustomers(selectedCompany.id)
    } else {
      setCustomers([])
    }
  }, [selectedCompany])

  const loadCustomers = async (companyId) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8080/api/v1/admin/companies/${companyId}/users`)
      if (response.ok) {
        const data = await response.json()
        setCustomers(data)
      }
    } catch (error) {
      console.error('Error loading customers:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCustomerChange = (e) => {
    const customerId = e.target.value
    const customer = customers.find(c => c.id == customerId)
    onCustomerSelect(customer || null)
  }

  return (
    <div className="sidebar-card">
      <h3>
        <span>👥</span>
        בחירת לקוח
      </h3>
      
      <div style={{ marginBottom: '16px', padding: '12px', background: '#f7fafc', borderRadius: '8px' }}>
        <div style={{ fontSize: '0.9rem', color: '#4a5568' }}>
          <strong>חברה נבחרת:</strong> {selectedCompany?.name}
        </div>
      </div>

      <div className="form-group">
        <label className="form-label">לקוח</label>
        <select 
          className="form-select"
          value={selectedCustomer?.id || ''}
          onChange={handleCustomerChange}
          disabled={!selectedCompany || loading}
        >
          <option value="">בחר לקוח...</option>
          {loading ? (
            <option disabled>טוען לקוחות...</option>
          ) : (
            customers.map(customer => (
              <option key={customer.id} value={customer.id}>
                {customer.name || customer.external_id}
              </option>
            ))
          )}
        </select>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '20px' }}>
        <button 
          className="btn btn-primary"
          onClick={onStartConversation}
          disabled={!selectedCustomer}
        >
          <span>💬</span>
          התחל שיחה חדשה
        </button>
        
        <button 
          className="btn btn-success"
          onClick={onCreateCustomer}
        >
          <span>➕</span>
          צור לקוח חדש
        </button>
      </div>

      {selectedCustomer && (
        <div style={{ marginTop: '16px', padding: '12px', background: '#f7fafc', borderRadius: '8px' }}>
          <div style={{ fontSize: '0.9rem', color: '#4a5568' }}>
            <strong>לקוח נבחר:</strong> {selectedCustomer.name || selectedCustomer.external_id}
          </div>
        </div>
      )}
    </div>
  )
}

export default CompanySelector

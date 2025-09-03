import React, { useState, useEffect } from 'react'

const CustomerProfile = ({ customer }) => {
  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (customer) {
      loadCustomerProfile(customer.id)
    }
  }, [customer])

  const loadCustomerProfile = async (customerId) => {
    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8080/api/v1/dev/customer/${customerId}/profile`)
      if (response.ok) {
        const data = await response.json()
        setProfile(data)
      }
    } catch (error) {
      console.error('Error loading customer profile:', error)
    } finally {
      setLoading(false)
    }
  }

  if (!customer) return null

  if (loading) {
    return (
      <div className="sidebar-card">
        <h3>
          <span>👤</span>
          פרופיל לקוח
        </h3>
        <div className="loading">
          <div className="spinner"></div>
          טוען פרופיל...
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="sidebar-card">
        <h3>
          <span>👤</span>
          פרופיל לקוח
        </h3>
        <div className="error">
          שגיאה בטעינת הפרופיל
        </div>
      </div>
    )
  }

  const getConversionStageColor = (stage) => {
    switch (stage) {
      case 'new': return '#ed8936'
      case 'interested': return '#4299e1'
      case 'qualified': return '#48bb78'
      case 'converted': return '#38a169'
      default: return '#a0aec0'
    }
  }

  const getConversionStageText = (stage) => {
    switch (stage) {
      case 'new': return 'לקוח חדש'
      case 'interested': return 'מתעניין'
      case 'qualified': return 'מוכשר'
      case 'converted': return 'הומר'
      default: return 'לא ידוע'
    }
  }

  return (
    <div className="sidebar-card">
      <h3>
        <span>👤</span>
        פרופיל לקוח
      </h3>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>שם:</strong>
          <span>{profile.name || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>גיל:</strong>
          <span>{profile.age || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>מיקום:</strong>
          <span>{profile.location || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>תפקיד:</strong>
          <span>{profile.occupation || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>תקציב:</strong>
          <span>{profile.budget_range || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>סטטוס משפחה:</strong>
          <span>{profile.family_status || 'לא צוין'}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>שיחות:</strong>
          <span>{profile.total_conversations || 0}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>הודעות:</strong>
          <span>{profile.total_messages || 0}</span>
        </div>
        
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <strong>שלב המרה:</strong>
          <span 
            style={{ 
              color: getConversionStageColor(profile.conversion_stage),
              fontWeight: '600',
              padding: '2px 8px',
              borderRadius: '12px',
              background: `${getConversionStageColor(profile.conversion_stage)}20`,
              fontSize: '0.85rem'
            }}
          >
            {getConversionStageText(profile.conversion_stage)}
          </span>
        </div>
      </div>

      {profile.interests && profile.interests.length > 0 && (
        <div style={{ marginTop: '16px' }}>
          <strong style={{ display: 'block', marginBottom: '8px' }}>תחומי עניין:</strong>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
            {profile.interests.map((interest, index) => (
              <span 
                key={index}
                style={{
                  background: '#e2e8f0',
                  color: '#4a5568',
                  padding: '4px 8px',
                  borderRadius: '12px',
                  fontSize: '0.8rem'
                }}
              >
                {interest}
              </span>
            ))}
          </div>
        </div>
      )}

      {profile.notes && (
        <div style={{ marginTop: '16px' }}>
          <strong style={{ display: 'block', marginBottom: '8px' }}>הערות:</strong>
          <div style={{ 
            background: '#f7fafc', 
            padding: '8px 12px', 
            borderRadius: '8px', 
            fontSize: '0.9rem',
            color: '#4a5568'
          }}>
            {profile.notes}
          </div>
        </div>
      )}
    </div>
  )
}

export default CustomerProfile

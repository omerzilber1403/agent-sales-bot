import React, { useState } from 'react'

const CreateCustomerModal = ({ company, onClose, onCustomerCreated }) => {
  const [formData, setFormData] = useState({
    name: '',
    phone: '',
    email: '',
    age: '',
    gender: '',
    location: '',
    occupation: '',
    budget_range: '',
    family_status: '',
    preferred_contact: '',
    interests: '',
    notes: ''
  })
  const [submitting, setSubmitting] = useState(false)

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!formData.name.trim()) {
      alert('שם הלקוח הוא שדה חובה')
      return
    }

    setSubmitting(true)
    try {
      const submitData = {
        ...formData,
        company_id: company.id,
        age: formData.age ? parseInt(formData.age) : null,
        interests: formData.interests ? formData.interests.split(',').map(s => s.trim()) : []
      }

      const response = await fetch('http://localhost:8080/api/v1/dev/customers', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(submitData)
      })

      if (response.ok) {
        const result = await response.json()
        alert(`לקוח נוצר בהצלחה! ID: ${result.user_id}`)
        onCustomerCreated({ id: result.user_id, name: formData.name })
      } else {
        const error = await response.json()
        alert('שגיאה ביצירת לקוח: ' + (error.detail || error.error || 'שגיאה לא ידועה'))
      }
    } catch (error) {
      alert('שגיאה ביצירת לקוח: ' + error.message)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 className="modal-title">צור לקוח חדש</h2>
          <button className="close-button" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="name">שם מלא *</label>
              <input
                type="text"
                id="name"
                name="name"
                className="form-input"
                value={formData.name}
                onChange={handleInputChange}
                required
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="phone">טלפון</label>
              <input
                type="tel"
                id="phone"
                name="phone"
                className="form-input"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="050-1234567"
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="email">אימייל</label>
              <input
                type="email"
                id="email"
                name="email"
                className="form-input"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="customer@example.com"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="age">גיל</label>
              <input
                type="number"
                id="age"
                name="age"
                className="form-input"
                value={formData.age}
                onChange={handleInputChange}
                min="1"
                max="120"
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="gender">מגדר</label>
              <select
                id="gender"
                name="gender"
                className="form-select"
                value={formData.gender}
                onChange={handleInputChange}
              >
                <option value="">בחר...</option>
                <option value="male">זכר</option>
                <option value="female">נקבה</option>
                <option value="other">אחר</option>
              </select>
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="location">מיקום</label>
              <input
                type="text"
                id="location"
                name="location"
                className="form-input"
                value={formData.location}
                onChange={handleInputChange}
                placeholder="עיר, רחוב"
              />
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="occupation">תפקיד/מקצוע</label>
              <input
                type="text"
                id="occupation"
                name="occupation"
                className="form-input"
                value={formData.occupation}
                onChange={handleInputChange}
                placeholder="מהנדס, מנהל, סטודנט"
              />
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="budget_range">תקציב</label>
              <select
                id="budget_range"
                name="budget_range"
                className="form-select"
                value={formData.budget_range}
                onChange={handleInputChange}
              >
                <option value="">בחר...</option>
                <option value="low">נמוך</option>
                <option value="medium">בינוני</option>
                <option value="high">גבוה</option>
              </select>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
            <div className="form-group">
              <label className="form-label" htmlFor="family_status">סטטוס משפחה</label>
              <select
                id="family_status"
                name="family_status"
                className="form-select"
                value={formData.family_status}
                onChange={handleInputChange}
              >
                <option value="">בחר...</option>
                <option value="single">רווק/רווקה</option>
                <option value="married">נשוי/נשואה</option>
                <option value="parent">הורה</option>
              </select>
            </div>
            
            <div className="form-group">
              <label className="form-label" htmlFor="preferred_contact">עדיפות קשר</label>
              <select
                id="preferred_contact"
                name="preferred_contact"
                className="form-select"
                value={formData.preferred_contact}
                onChange={handleInputChange}
              >
                <option value="">בחר...</option>
                <option value="phone">טלפון</option>
                <option value="email">אימייל</option>
                <option value="whatsapp">ווטסאפ</option>
              </select>
            </div>
          </div>

          <div className="form-group" style={{ marginBottom: '16px' }}>
            <label className="form-label" htmlFor="interests">תחומי עניין (מופרדים בפסיקים)</label>
            <input
              type="text"
              id="interests"
              name="interests"
              className="form-input"
              value={formData.interests}
              onChange={handleInputChange}
              placeholder="ספורט, מוזיקה, טכנולוגיה"
            />
          </div>

          <div className="form-group" style={{ marginBottom: '24px' }}>
            <label className="form-label" htmlFor="notes">הערות</label>
            <textarea
              id="notes"
              name="notes"
              className="form-input"
              value={formData.notes}
              onChange={handleInputChange}
              rows="3"
              placeholder="הערות נוספות על הלקוח..."
              style={{ resize: 'vertical' }}
            />
          </div>

          <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
            <button 
              type="submit" 
              className="btn btn-success"
              disabled={submitting}
            >
              {submitting ? (
                <>
                  <div className="spinner"></div>
                  יוצר...
                </>
              ) : (
                <>
                  <span>✅</span>
                  צור לקוח
                </>
              )}
            </button>
            
            <button 
              type="button" 
              className="btn btn-secondary"
              onClick={onClose}
              disabled={submitting}
            >
              <span>❌</span>
              ביטול
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateCustomerModal

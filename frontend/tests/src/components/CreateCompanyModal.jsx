import React, { useState } from 'react'

const CreateCompanyModal = ({ isOpen, onClose, onCompanyCreated }) => {
  const [formData, setFormData] = useState({
    // Core - חובה
    name: '',
    brand_aliases: '',
    timezone: 'Asia/Jerusalem',
    locale: 'he-IL',
    currency: 'ILS',
    business_type: 'B2B',
    
    // Brand Voice
    brand_voice: {
      style: 'warm, professional, short_by_default',
      short_mode_default: true,
      long_mode_triggers: '',
      forbidden_words: '',
      emoji_policy: 'mirror_user',
      closing_tone: 'decisive_single_cta'
    },
    
    one_line_value: '',
    
    // ICP
    icp: {
      industries: '',
      company_size: '',
      buyer_roles: ''
    },
    
    pain_points: '',
    
    // Products
    products: [
      { id: 'starter', name: '', summary: '', base_price: '', addons: '' }
    ],
    
    // Pricing Policy
    pricing_policy: {
      currency: 'ILS',
      plans: [
        { plan_id: 'starter', from: '', to: '' }
      ],
      discount_rules: '',
      addons: ''
    },
    
    // CTA
    cta_type: 'booking_link',
    booking_link: '',
    meeting_length_min: 15,
    
    // Qualification Rules
    qualification_rules: {
      required: '',
      bant: {
        budget_hint: true,
        authority_hint: true,
        need: true,
        timeline: true
      }
    },
    
    // Objections Playbook
    objections_playbook: '',
    
    // Handoff Rules
    handoff_rules: {
      triggers: '',
      target_queue: 'sales-team',
      user_msg_on_handoff: 'מעביר/ה לנציג/ה אנושי/ת ויחזרו אליך ממש בקרוב.'
    },
    
    // Custom fields for company-specific data collection
    custom_fields: {
      description: '',
      fields: {}
    }
  })

  const [currentStep, setCurrentStep] = useState(1)
  const [loading, setLoading] = useState(false)

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.')
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value
        }
      }))
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value
      }))
    }
  }

  const handleArrayInputChange = (field, value) => {
    const arrayValue = value.split(',').map(item => item.trim()).filter(item => item)
    setFormData(prev => ({
      ...prev,
      [field]: arrayValue
    }))
  }

  const addProduct = () => {
    setFormData(prev => ({
      ...prev,
      products: [...prev.products, { id: '', name: '', summary: '', base_price: '', addons: '' }]
    }))
  }

  const updateProduct = (index, field, value) => {
    setFormData(prev => ({
      ...prev,
      products: prev.products.map((product, i) => 
        i === index ? { ...product, [field]: value } : product
      )
    }))
  }

  const removeProduct = (index) => {
    setFormData(prev => ({
      ...prev,
      products: prev.products.filter((_, i) => i !== index)
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)

    try {
      // Process form data before sending
      const processedData = {
        ...formData,
        // Convert brand_aliases string to array
        brand_aliases: formData.brand_aliases ? 
          (Array.isArray(formData.brand_aliases) ? formData.brand_aliases : formData.brand_aliases.split(',').map(item => item.trim()).filter(item => item)) : 
          [],
        
        // Convert pain_points string to array
        pain_points: formData.pain_points ? 
          (Array.isArray(formData.pain_points) ? formData.pain_points : formData.pain_points.split(',').map(item => item.trim()).filter(item => item)) : 
          [],
        
        // Convert objections_playbook string to object
        objections_playbook: formData.objections_playbook ? 
          (() => {
            try {
              return JSON.parse(formData.objections_playbook)
            } catch {
              // If not valid JSON, create object from key:value pairs
              const pairs = formData.objections_playbook.split(',').map(pair => pair.trim())
              const obj = {}
              pairs.forEach(pair => {
                const [key, ...valueParts] = pair.split(':')
                if (key && valueParts.length > 0) {
                  obj[key.trim()] = valueParts.join(':').trim()
                }
              })
              return obj
            }
          })() : 
          {},
        
        // Convert handoff_rules.triggers string to array
        handoff_rules: {
          ...formData.handoff_rules,
          triggers: formData.handoff_rules.triggers ? 
            (Array.isArray(formData.handoff_rules.triggers) ? formData.handoff_rules.triggers : formData.handoff_rules.triggers.split(',').map(item => item.trim()).filter(item => item)) : 
            []
        },
        
        // Convert brand_voice.forbidden_words string to array
        brand_voice: {
          ...formData.brand_voice,
          forbidden_words: formData.brand_voice.forbidden_words ? 
            (Array.isArray(formData.brand_voice.forbidden_words) ? formData.brand_voice.forbidden_words : formData.brand_voice.forbidden_words.split(',').map(item => item.trim()).filter(item => item)) : 
            []
        },
        
        // Convert ICP fields
        icp: {
          ...formData.icp,
          industries: formData.icp.industries ? 
            (Array.isArray(formData.icp.industries) ? formData.icp.industries : formData.icp.industries.split(',').map(item => item.trim()).filter(item => item)) : 
            [],
          buyer_roles: formData.icp.buyer_roles ? 
            (Array.isArray(formData.icp.buyer_roles) ? formData.icp.buyer_roles : formData.icp.buyer_roles.split(',').map(item => item.trim()).filter(item => item)) : 
            []
        }
      }

      console.log('Sending processed data:', processedData)

      const response = await fetch('http://localhost:8080/api/v1/admin/companies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(processedData)
      })

      if (response.ok) {
        const newCompany = await response.json()
        onCompanyCreated(newCompany)
        onClose()
        // Reset form
        setFormData({
          name: '',
          brand_aliases: '',
          timezone: 'Asia/Jerusalem',
          locale: 'he-IL',
          currency: 'ILS',
          brand_voice: {
            style: 'warm, professional, short_by_default',
            short_mode_default: true,
            long_mode_triggers: '',
            forbidden_words: '',
            emoji_policy: 'mirror_user',
            closing_tone: 'decisive_single_cta'
          },
          one_line_value: '',
          icp: {
            industries: '',
            company_size: '',
            buyer_roles: ''
          },
          pain_points: '',
          products: [
            { id: 'starter', name: '', summary: '', base_price: '', addons: '' }
          ],
          pricing_policy: {
            currency: 'ILS',
            plans: [
              { plan_id: 'starter', from: '', to: '' }
            ],
            discount_rules: '',
            addons: ''
          },
          cta_type: 'booking_link',
          booking_link: '',
          meeting_length_min: 15,
          qualification_rules: {
            required: '',
            bant: {
              budget_hint: true,
              authority_hint: true,
              need: true,
              timeline: true
            }
          },
          objections_playbook: '',
          handoff_rules: {
            triggers: '',
            target_queue: 'sales-team',
            user_msg_on_handoff: 'מעביר/ה לנציג/ה אנושי/ת ויחזרו אליך ממש בקרוב.'
          }
        })
        setCurrentStep(1)
      } else {
        console.error('Error creating company:', await response.text())
      }
    } catch (error) {
      console.error('Error creating company:', error)
    } finally {
      setLoading(false)
    }
  }

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1)
    }
  }

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
    }
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay">
      <div className="modal-content large-modal">
        <div className="modal-header">
          <h2>צור חברה חדשה</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* Step 1: Core Information */}
          {currentStep === 1 && (
            <div className="form-step">
              <h3>מידע בסיסי (חובה)</h3>
              
              <div className="form-group">
                <label>שם החברה *</label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => handleInputChange('name', e.target.value)}
                  required
                />
              </div>

              <div className="form-group">
                <label>כינויים/שמות נוספים (מופרדים בפסיקים)</label>
                <input
                  type="text"
                  value={formData.brand_aliases}
                  onChange={(e) => handleInputChange('brand_aliases', e.target.value)}
                  placeholder="Acme, AcmeD"
                />
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label>אזור זמן</label>
                  <select
                    value={formData.timezone}
                    onChange={(e) => handleInputChange('timezone', e.target.value)}
                  >
                    <option value="Asia/Jerusalem">Asia/Jerusalem</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>שפה</label>
                  <select
                    value={formData.locale}
                    onChange={(e) => handleInputChange('locale', e.target.value)}
                  >
                    <option value="he-IL">עברית</option>
                    <option value="en-US">English</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>מטבע</label>
                  <select
                    value={formData.currency}
                    onChange={(e) => handleInputChange('currency', e.target.value)}
                  >
                    <option value="ILS">₪ (שקל)</option>
                    <option value="USD">$ (דולר)</option>
                    <option value="EUR">€ (יורו)</option>
                  </select>
                </div>
              </div>

              <div className="form-group">
                <label>סוג עסק</label>
                <div className="business-type-toggle">
                  <label className="toggle-option">
                    <input
                      type="radio"
                      name="business_type"
                      value="B2B"
                      checked={formData.business_type === 'B2B'}
                      onChange={(e) => handleInputChange('business_type', e.target.value)}
                    />
                    <span className="toggle-label">
                      <strong>B2B</strong> - עסק לעסק
                      <small>מוכרים לחברות אחרות</small>
                    </span>
                  </label>
                  <label className="toggle-option">
                    <input
                      type="radio"
                      name="business_type"
                      value="B2C"
                      checked={formData.business_type === 'B2C'}
                      onChange={(e) => handleInputChange('business_type', e.target.value)}
                    />
                    <span className="toggle-label">
                      <strong>B2C</strong> - עסק לצרכן
                      <small>מוכרים ללקוחות פרטיים</small>
                    </span>
                  </label>
                </div>
              </div>

              <div className="form-group">
                <label>הצעת ערך במשפט אחד *</label>
                <textarea
                  value={formData.one_line_value}
                  onChange={(e) => handleInputChange('one_line_value', e.target.value)}
                  placeholder="יותר לידים איכותיים בפחות זמן – עם בוט מכירות שמחליף התכתבות ידנית."
                  required
                />
              </div>

              <div className="form-group">
                <label>ענפים (מופרדים בפסיקים)</label>
                <input
                  type="text"
                  value={formData.icp.industries}
                  onChange={(e) => handleInputChange('icp.industries', e.target.value)}
                  placeholder="שירותים מקומיים, SaaS B2B"
                />
              </div>

              <div className="form-group">
                <label>גודל חברה</label>
                <input
                  type="text"
                  value={formData.icp.company_size}
                  onChange={(e) => handleInputChange('icp.company_size', e.target.value)}
                  placeholder="2-200"
                />
              </div>

              <div className="form-group">
                <label>תפקידי קונה (מופרדים בפסיקים)</label>
                <input
                  type="text"
                  value={formData.icp.buyer_roles}
                  onChange={(e) => handleInputChange('icp.buyer_roles', e.target.value)}
                  placeholder="Owner, Marketing"
                />
              </div>

              <div className="form-group">
                <label>כאבים מרכזיים (מופרדים בפסיקים)</label>
                <textarea
                  value={formData.pain_points}
                  onChange={(e) => handleArrayInputChange('pain_points', e.target.value)}
                  placeholder="זמן מענה איטי, זליגת לידים, חוסר עקביות במסרים"
                />
              </div>
            </div>
          )}

          {/* Step 2: Products & Pricing */}
          {currentStep === 2 && (
            <div className="form-step">
              <h3>מוצרים ומחירים</h3>
              
              <div className="products-section">
                <h4>מוצרים/חבילות</h4>
                {formData.products.map((product, index) => (
                  <div key={index} className="product-item">
                    <div className="form-row">
                      <div className="form-group">
                        <label>מזהה מוצר</label>
                        <input
                          type="text"
                          value={product.id}
                          onChange={(e) => updateProduct(index, 'id', e.target.value)}
                          placeholder="starter"
                        />
                      </div>
                      <div className="form-group">
                        <label>שם המוצר</label>
                        <input
                          type="text"
                          value={product.name}
                          onChange={(e) => updateProduct(index, 'name', e.target.value)}
                          placeholder="חבילת בסיס"
                        />
                      </div>
                    </div>
                    
                    <div className="form-group">
                      <label>תיאור קצר</label>
                      <input
                        type="text"
                        value={product.summary}
                        onChange={(e) => updateProduct(index, 'summary', e.target.value)}
                        placeholder="בוט צ'אט + הובלת לידים"
                      />
                    </div>
                    
                    <div className="form-row">
                      <div className="form-group">
                        <label>מחיר בסיס</label>
                        <input
                          type="number"
                          value={product.base_price}
                          onChange={(e) => updateProduct(index, 'base_price', e.target.value)}
                          placeholder="900"
                        />
                      </div>
                      <div className="form-group">
                        <label>תוספות (מופרדות בפסיקים)</label>
                        <input
                          type="text"
                          value={product.addons}
                          onChange={(e) => updateProduct(index, 'addons', e.target.value)}
                          placeholder="קלנדר"
                        />
                      </div>
                    </div>
                    
                    {formData.products.length > 1 && (
                      <button
                        type="button"
                        className="remove-btn"
                        onClick={() => removeProduct(index)}
                      >
                        הסר מוצר
                      </button>
                    )}
                  </div>
                ))}
                
                <button type="button" className="add-btn" onClick={addProduct}>
                  הוסף מוצר
                </button>
              </div>

              <div className="form-group">
                <label>קישור לקביעת פגישה</label>
                <input
                  type="url"
                  value={formData.booking_link}
                  onChange={(e) => handleInputChange('booking_link', e.target.value)}
                  placeholder="https://cal.example.com/acme"
                />
              </div>

              <div className="form-group">
                <label>אורך פגישה (דקות)</label>
                <input
                  type="number"
                  value={formData.meeting_length_min}
                  onChange={(e) => handleInputChange('meeting_length_min', e.target.value)}
                />
              </div>
            </div>
          )}

          {/* Step 3: Sales Rules */}
          {currentStep === 3 && (
            <div className="form-step">
              <h3>כללי מכירות</h3>
              
              <div className="form-group">
                <label>התנגדויות נפוצות ותשובות</label>
                <textarea
                  value={formData.objections_playbook}
                  onChange={(e) => handleInputChange('objections_playbook', e.target.value)}
                  placeholder='{"יקר": "מבין. לרוב זה מחזיר את עצמו תוך ~2-3 חודשים. נתחיל בפיילוט קטן כדי למדוד?", "אין זמן": "לוקח ~20 דקות להתחיל, אנחנו מקימים עבורך. נקבע 10 דקות?"}'
                  rows={4}
                />
              </div>

              <div className="form-group">
                <label>מתי להעביר לנציג אנושי (מופרדים בפסיקים)</label>
                <input
                  type="text"
                  value={formData.handoff_rules.triggers}
                  onChange={(e) => handleInputChange('handoff_rules.triggers', e.target.value)}
                  placeholder="בקשת הנחה חריגה, תמיכה טכנית עמוקה, שפה לא נאותה"
                />
              </div>

              <div className="form-group">
                <label>הודעה בעת העברה לנציג</label>
                <input
                  type="text"
                  value={formData.handoff_rules.user_msg_on_handoff}
                  onChange={(e) => handleInputChange('handoff_rules.user_msg_on_handoff', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label>מילים אסורות (מופרדות בפסיקים)</label>
                <input
                  type="text"
                  value={formData.brand_voice.forbidden_words}
                  onChange={(e) => handleInputChange('brand_voice.forbidden_words', e.target.value)}
                  placeholder="זול מדי, 100% מובטח"
                />
              </div>
            </div>
          )}

          <div className="modal-footer">
            <div className="step-indicator">
              שלב {currentStep} מתוך 3
            </div>
            
            <div className="form-actions">
              {currentStep > 1 && (
                <button type="button" onClick={prevStep} className="btn btn-secondary">
                  קודם
                </button>
              )}
              
              {currentStep < 3 ? (
                <button type="button" onClick={nextStep} className="btn btn-primary">
                  הבא
                </button>
              ) : (
                <button type="submit" className="btn btn-success" disabled={loading}>
                  {loading ? 'יוצר...' : 'צור חברה'}
                </button>
              )}
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}

export default CreateCompanyModal

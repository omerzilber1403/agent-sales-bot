import React, { useState, useEffect, useRef } from 'react'
import './DemoInterface.css'

const DemoInterface = ({ company, onStatsUpdate }) => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [typing, setTyping] = useState(false)
  const [messageStatus, setMessageStatus] = useState('')
  const [messageCount, setMessageCount] = useState(0)
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const [currentRating, setCurrentRating] = useState(null)
  const [currentFeedback, setCurrentFeedback] = useState('')
  const [showRatingModal, setShowRatingModal] = useState(false)
  const [ratingData, setRatingData] = useState([])
  const [lastUserMessage, setLastUserMessage] = useState('')
  const [lastBotMessage, setLastBotMessage] = useState('')
  const [sessionId] = useState(`demo_${Date.now()}`)
  const messagesEndRef = useRef(null)

  // Demo customer data
  const demoCustomer = {
    name: "דמו לקוח",
    external_id: "demo_customer",
    phone: "050-1234567",
    email: "demo@example.com"
  }

  useEffect(() => {
    scrollToBottom()
    setMessageCount(messages.length)
  }, [messages])

  // Check connection status
  useEffect(() => {
    const checkConnection = async () => {
      try {
        const response = await fetch('http://localhost:8080/health')
        setConnectionStatus(response.ok ? 'connected' : 'disconnected')
      } catch {
        setConnectionStatus('disconnected')
      }
    }
    
    checkConnection()
    const interval = setInterval(checkConnection, 30000)
    return () => clearInterval(interval)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || sending) return

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
      status: 'sending'
    }

    setMessages(prev => [...prev, userMessage])
    setLastUserMessage(inputMessage) // Save user message for rating modal
    setInputMessage('')
    setSending(true)
    setMessageStatus('שולח הודעה...')
    setTyping(true)

    try {
      const response = await fetch('http://localhost:8080/api/v1/agent/reply', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: inputMessage,
          company_id: company.id,
          customer_id: demoCustomer.external_id,
          session_id: sessionId,
          channel: 'demo'
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        setMessageStatus('מקבל תשובה...')
        
        const botMessage = {
          id: Date.now() + 1,
          role: 'bot',
          content: data.text,
          timestamp: new Date(),
          handoff: data.handoff,
          handoffReason: data.handoff_reason,
          tone: data.tone,
          executionPath: data.execution_path,
          status: 'delivered',
          quality: data.handoff ? 'handoff' : 'good'
        }

        setMessages(prev => [...prev, botMessage])
        setLastBotMessage(data.text) // Save bot message for rating modal
        
        // Show rating modal for bot messages after a delay
        if (data.text && !data.handoff) {
          setTimeout(() => {
            setShowRatingModal(true)
          }, 3000) // 3 seconds delay to read the response
        }
        
        if (onStatsUpdate) {
          onStatsUpdate({
            messages: messages.length + 2,
            handoffs: data.handoff ? 1 : 0,
            avgResponseTime: Date.now() - userMessage.timestamp.getTime()
          })
        }
      } else {
        throw new Error('Failed to send message')
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: 'מצטער, אירעה שגיאה. נסה שוב.',
        timestamp: new Date(),
        status: 'error',
        quality: 'error'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setSending(false)
      setTyping(false)
      setMessageStatus('')
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const submitRating = () => {
    if (currentRating && messages.length > 0) {
      const lastBotMessage = [...messages].reverse().find(msg => msg.role === 'bot')
      
      const rating = {
        id: Date.now(),
        messageId: lastBotMessage?.id,
        rating: currentRating,
        feedback: currentFeedback,
        timestamp: new Date(),
        companyId: company.id,
        sessionId: sessionId
      }

      setRatingData(prev => [...prev, rating])
      setCurrentRating(null)
      setCurrentFeedback('')
      setShowRatingModal(false)

      // Send rating to backend
      fetch('http://localhost:8080/api/v1/feedback/rating', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(rating)
      }).catch(console.error)
    }
  }

  const getRatingStats = () => {
    if (ratingData.length === 0) return { avg: 0, count: 0 }
    
    const total = ratingData.reduce((sum, r) => sum + r.rating, 0)
    return {
      avg: (total / ratingData.length).toFixed(1),
      count: ratingData.length
    }
  }

  const stats = getRatingStats()

  return (
    <div className="demo-container">
      <div className="demo-header">
        <div className="demo-title">
          <span className="demo-icon">🧪</span>
          ממשק דמו - {company.name}
          {messageCount > 0 && (
            <span className="message-count-badge">
              {messageCount} הודעות
            </span>
          )}
        </div>
        <div className="demo-stats">
          <div className="rating-stats">
            <span className="rating-label">דירוג ממוצע:</span>
            <span className="rating-value">{stats.avg}/5</span>
            <span className="rating-count">({stats.count} דירוגים)</span>
          </div>
          <div className={`connection-status ${connectionStatus}`}>
            <span className="status-dot"></span>
            {connectionStatus === 'connected' ? 'מחובר' : 'מנותק'}
          </div>
        </div>
      </div>

      <div className="demo-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🤖'}
            </div>
            <div className="message-content">
              <div>{message.content}</div>
              <div className="message-meta">
                <span>{message.timestamp.toLocaleTimeString('he-IL', { 
                  hour: '2-digit', 
                  minute: '2-digit' 
                })}</span>
                {message.handoff && (
                  <span className="handoff-badge">HANDOFF</span>
                )}
                {message.tone && (
                  <span className="tone-badge">{message.tone}</span>
                )}
                {message.quality && (
                  <span className={`quality-badge ${message.quality}`}>
                    {message.quality === 'handoff' ? 'HANDOFF' : '✓'}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        {typing && (
          <div className="typing-indicator">
            <div className="typing-dots">
              <span></span>
              <span></span>
              <span></span>
            </div>
            <span className="typing-text">{messageStatus}</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="demo-input">
        <div className="input-container">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="כתוב הודעה לבדיקת הבוט..."
            disabled={sending}
            className="message-input"
          />
          <button
            onClick={sendMessage}
            disabled={!inputMessage.trim() || sending}
            className="send-button"
          >
            {sending ? '⏳' : '📤'}
          </button>
        </div>
      </div>

      {/* Rating Modal */}
      {showRatingModal && (
        <div className="rating-modal-overlay">
          <div className="rating-modal">
            <div className="rating-modal-header">
              <h3>דרג את התשובה</h3>
              <button 
                className="close-button"
                onClick={() => setShowRatingModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="rating-modal-content">
              {/* Show the conversation context */}
              <div className="conversation-context">
                <div className="context-message user-message">
                  <div className="context-avatar">👤</div>
                  <div className="context-content">
                    <div className="context-label">השאלה שלך:</div>
                    <div className="context-text">{lastUserMessage}</div>
                  </div>
                </div>
                <div className="context-message bot-message">
                  <div className="context-avatar">🤖</div>
                  <div className="context-content">
                    <div className="context-label">תשובת הבוט:</div>
                    <div className="context-text">{lastBotMessage}</div>
                  </div>
                </div>
              </div>
              
              <div className="rating-section">
                <div className="rating-question">איך תדרג את התשובה?</div>
                <div className="rating-stars">
                  {[1, 2, 3, 4, 5].map((star) => (
                    <button
                      key={star}
                      className={`star ${currentRating >= star ? 'active' : ''}`}
                      onClick={() => setCurrentRating(star)}
                    >
                      ⭐
                    </button>
                  ))}
                </div>
                <div className="rating-labels">
                  <span>גרוע</span>
                  <span>מעולה</span>
                </div>
              </div>
              
              <div className="feedback-section">
                <label className="feedback-label">הערות והצעות שיפור (אופציונלי):</label>
                <textarea
                  value={currentFeedback}
                  onChange={(e) => setCurrentFeedback(e.target.value)}
                  placeholder="מה היה טוב? מה אפשר לשפר? איך הבוט יכול לעזור יותר?"
                  className="feedback-input"
                />
              </div>
              
              <div className="rating-actions">
                <button 
                  className="skip-button"
                  onClick={() => setShowRatingModal(false)}
                >
                  דלג
                </button>
                <button 
                  className="submit-button"
                  onClick={submitRating}
                  disabled={!currentRating}
                >
                  שלח דירוג
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default DemoInterface

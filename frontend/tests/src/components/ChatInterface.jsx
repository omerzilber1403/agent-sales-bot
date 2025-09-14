import React, { useState, useEffect, useRef } from 'react'

const ChatInterface = ({ company, customer, sessionId, onStatsUpdate }) => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [sending, setSending] = useState(false)
  const [executionPath, setExecutionPath] = useState([])
  const [typing, setTyping] = useState(false)
  const [messageStatus, setMessageStatus] = useState('')
  const [messageCount, setMessageCount] = useState(0)
  const [newMessageCount, setNewMessageCount] = useState(0)
  const [connectionStatus, setConnectionStatus] = useState('connected')
  const messagesEndRef = useRef(null)

  useEffect(() => {
    if (sessionId) {
      // Don't send automatic welcome message - wait for user to send first message
      setMessages([])
      setExecutionPath(['שיחה חדשה התחילה'])
    }
  }, [sessionId, company])

  useEffect(() => {
    scrollToBottom()
    setMessageCount(messages.length)
    
    // Count new messages (not user messages)
    const botMessages = messages.filter(msg => msg.role === 'bot')
    setNewMessageCount(botMessages.length)
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
    const interval = setInterval(checkConnection, 30000) // Check every 30 seconds
    return () => clearInterval(interval)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || sending) return

    const messageText = inputMessage.trim()
    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: messageText,
      timestamp: new Date(),
      status: 'sent'
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setSending(true)
    setTyping(true)
    setMessageStatus('שולח הודעה...')

    try {
      const response = await fetch('http://localhost:8080/api/v1/agent/reply', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          company_id: company.id,
          user_id: customer.id.toString(),
          session_id: sessionId,
          message: messageText,
          channel: 'dev'
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
        
        if (data.execution_path) {
          setExecutionPath(data.execution_path)
        }

        // Update stats
        if (onStatsUpdate) {
          onStatsUpdate()
        }
        
        setMessageStatus('')
      } else {
        const errorMessage = {
          id: Date.now() + 1,
          role: 'bot',
          content: 'מצטער, יש בעיה טכנית. אנא נסה שוב מאוחר יותר.',
          timestamp: new Date(),
          isError: true
        }
        setMessages(prev => [...prev, errorMessage])
      }
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessage = {
        id: Date.now() + 1,
        role: 'bot',
        content: 'שגיאה בשליחת ההודעה',
        timestamp: new Date(),
        isError: true
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

  const getMessageAvatar = (role) => {
    return role === 'user' ? '👤' : '🤖'
  }

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('he-IL', {
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!company || !customer) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-title">
            <span className="chat-icon">💬</span>
            צ'אט
          </div>
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: '#718096',
          fontSize: '1.1rem'
        }}>
          בחר חברה ולקוח כדי להתחיל שיחה
        </div>
      </div>
    )
  }

  if (!sessionId) {
    return (
      <div className="chat-container">
        <div className="chat-header">
          <div className="chat-title">
            <span className="chat-icon">💬</span>
            צ'אט - {customer.name || customer.external_id}
          </div>
        </div>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center', 
          justifyContent: 'center', 
          height: '100%',
          color: '#718096',
          fontSize: '1.1rem'
        }}>
          לחץ על "התחל שיחה חדשה" כדי להתחיל
        </div>
      </div>
    )
  }

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-title">
          <span className="chat-icon">💬</span>
          צ'אט - {customer.name || customer.external_id}
          {messageCount > 0 && (
            <span className="message-count-badge">
              {messageCount} הודעות
            </span>
          )}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          {executionPath.length > 0 && (
            <div style={{ 
              fontSize: '0.85rem', 
              color: '#718096',
              background: '#f7fafc',
              padding: '4px 8px',
              borderRadius: '12px'
            }}>
              מסלול: {executionPath.join(' → ')}
            </div>
          )}
          <div className={`connection-status ${connectionStatus}`}>
            <span className="status-dot"></span>
            {connectionStatus === 'connected' ? 'מחובר' : 'מנותק'}
          </div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((message) => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {getMessageAvatar(message.role)}
            </div>
            <div className="message-content">
              <div>{message.content}</div>
              <div style={{ 
                fontSize: '0.75rem', 
                opacity: 0.7, 
                marginTop: '4px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}>
                <span>{formatTime(message.timestamp)}</span>
                {message.handoff && (
                  <span style={{ 
                    background: '#fed7d7',
                    color: '#c53030',
                    padding: '2px 6px',
                    borderRadius: '8px',
                    fontSize: '0.7rem',
                    fontWeight: '600'
                  }}>
                    HANDOFF
                  </span>
                )}
                {message.tone && (
                  <span style={{ 
                    background: '#e6fffa',
                    color: '#319795',
                    padding: '2px 6px',
                    borderRadius: '8px',
                    fontSize: '0.7rem'
                  }}>
                    {message.tone}
                  </span>
                )}
                {message.quality && (
                  <span style={{ 
                    background: message.quality === 'handoff' ? '#fed7d7' : '#c6f6d5',
                    color: message.quality === 'handoff' ? '#c53030' : '#2f855a',
                    padding: '2px 6px',
                    borderRadius: '8px',
                    fontSize: '0.7rem',
                    fontWeight: '600'
                  }}>
                    {message.quality === 'handoff' ? 'HANDOFF' : '✓'}
                  </span>
                )}
              </div>
            </div>
          </div>
        ))}
        {typing && (
          <div className="message bot">
            <div className="message-avatar">🤖</div>
            <div className="message-content">
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
                {messageStatus || 'כותב תשובה...'}
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input">
        <input
          type="text"
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="הקלד הודעה..."
          disabled={sending}
        />
        <button 
          className="send-button"
          onClick={sendMessage}
          disabled={!inputMessage.trim() || sending}
        >
          <span>📤</span>
          שלח
        </button>
      </div>
    </div>
  )
}

export default ChatInterface

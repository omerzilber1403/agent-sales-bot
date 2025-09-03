import React from 'react'

const StatsPanel = ({ stats }) => {
  return (
    <div className="stats-panel">
      <div className="stat-card">
        <div className="stat-number">{stats.totalMessages || 0}</div>
        <div className="stat-label">הודעות</div>
      </div>
      
      <div className="stat-card">
        <div className="stat-number">{stats.handoffs || 0}</div>
        <div className="stat-label">Handoffs</div>
      </div>
      
      <div className="stat-card">
        <div className="stat-number">{stats.conversations || 0}</div>
        <div className="stat-label">שיחות</div>
      </div>
    </div>
  )
}

export default StatsPanel

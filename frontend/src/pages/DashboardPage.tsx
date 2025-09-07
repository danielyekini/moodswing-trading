import { useState } from 'react'
import StockChart from '../components/StockChart'
import NewsFeed from '../components/NewsFeed'
import './DashboardPage.css'

function DashboardPage() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'ticker-analysis'>('dashboard')
  
  const ticker = 'AAPL' // For now, hardcoded to AAPL



  return (
    <div className="dashboard-page">
      {/* Navigation Bar */}
      <nav className="dashboard-navbar">
        <div className="navbar-content">
          {/* Logo */}
          <div className="navbar-logo">
            <div className="logo-icon">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <path d="M8 20L16 12L24 20" stroke="#3B82F6" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 14L16 6L24 14" stroke="#06B6D4" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
            </div>
            <span className="logo-text">MoodSwing Trading</span>
          </div>

          {/* Navigation Tabs */}
          <div className="navbar-tabs">
            <button 
              className={`nav-tab ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              Dashboard
            </button>
            <button 
              className={`nav-tab ${activeTab === 'ticker-analysis' ? 'active' : ''}`}
              onClick={() => setActiveTab('ticker-analysis')}
            >
              Ticker Analysis
            </button>
          </div>

          {/* Search */}
          <div className="navbar-search">
            <div className="search-container">
              <svg className="search-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <path d="M17.5 17.5L13.875 13.875M15.8333 9.16667C15.8333 12.8486 12.8486 15.8333 9.16667 15.8333C5.48477 15.8333 2.5 12.8486 2.5 9.16667C2.5 5.48477 5.48477 2.5 9.16667 2.5C12.8486 2.5 15.8333 5.48477 15.8333 9.16667Z" stroke="#9CA3AF" strokeWidth="1.67" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <input 
                type="text" 
                placeholder="Search" 
                className="search-input"
              />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      {activeTab === 'dashboard' ? (
        <div className="dashboard-content">
          {/* Top Row: Stock Chart + Sentiment Gauge */}
          <div className="top-row">
            <StockChart ticker={ticker} />
            <div className="placeholder-div card sentiment-gauge" data-name="Sentiment Gauge">
              <span>Sentiment Gauge - Circular gauge showing 62, Moderately Bullish</span>
            </div>
          </div>

          {/* Bottom Row: News Feed + Sector Overview + Prediction */}
          <div className="bottom-row">
            <NewsFeed ticker={ticker} />
            <div className="placeholder-div card sector-overview" data-name="Sector Overview">
              <span>Sector Overview - AAPL, TSLA, AMZN, GOOGL with prices and changes</span>
            </div>
            <div className="placeholder-div card prediction" data-name="Prediction">
              <span>Prediction - Price forecasts for AAPL, TSLA, AMZN, GOOGL with trend charts</span>
            </div>
          </div>
        </div>
      ) : (
        <div className="ticker-analysis-content">
          <div className="placeholder-div card full-width-card" data-name="Ticker Analysis">
            <span>Ticker Analysis - Advanced analysis tools and deep dive charts</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default DashboardPage

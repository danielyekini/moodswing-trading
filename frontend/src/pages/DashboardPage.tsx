import './DashboardPage.css'

function DashboardPage() {
  return (
    <div className="dashboard-page">
      {/* Navigation Bar */}
      <div className="placeholder-div dashboard-navbar" data-name="Dashboard Navbar">
        <span>Dashboard Navbar - Logo, Tabs (Dashboard, Ticker Analysis, Market Mood, API Explorer), Search, User</span>
      </div>

      {/* Main Content Area */}
      <div className="dashboard-content">
        {/* Left Column */}
        <div className="left-column">
          {/* Primary Chart/Stock Info */}
          <div className="placeholder-div primary-chart" data-name="Primary Chart">
            <span>AAPL Chart - Price: 175.43, Today +0.23%, Candlestick Chart</span>
          </div>

          {/* News Feed */}
          <div className="placeholder-div news-feed" data-name="News Feed">
            <span>News Feed - Latest news items with sentiment indicators</span>
          </div>
        </div>

        {/* Right Column */}
        <div className="right-column">
          {/* Sentiment Gauge */}
          <div className="placeholder-div sentiment-gauge" data-name="Sentiment Gauge">
            <span>Sentiment Gauge - Circular gauge showing 62, Moderately Bullish</span>
          </div>

          {/* Market Overview */}
          <div className="placeholder-div market-overview" data-name="Market Overview">
            <span>Market Overview - AAPL, TSLA, AMZN, GOOGL with prices and changes</span>
          </div>

          {/* Prediction */}
          <div className="placeholder-div prediction" data-name="Prediction">
            <span>Prediction - Price forecasts for AAPL, TSLA, AMZN, GOOGL with trend charts</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default DashboardPage

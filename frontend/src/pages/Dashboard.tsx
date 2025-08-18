import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-page">
      <div className="navbar">
        <div className="navbar-brand">MoodSwing Trading</div>
        <div className="navbar-nav">
          <div className="nav-item active">Dashboard</div>
          <div className="nav-item">Ticker Analysis</div>
          <div className="nav-item">Market Mood</div>
          <div className="nav-item">API Explorer</div>
        </div>
        <div className="navbar-actions">
          <div className="search-box">Search</div>
          <div className="user-profile">User</div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="left-panel">
          <div className="stock-price-section">
            <div className="stock-symbol">AAPL</div>
            <div className="stock-price">175.43</div>
            <div className="stock-change">Today + 0.23%</div>
          </div>

          <div className="main-chart">
            <div className="chart-placeholder">Live chart preview</div>
          </div>

          <div className="sentiment-analysis">
            <h3>Sentiment + LLM Inference</h3>
            <div className="sentiment-points">
              <div className="sentiment-point">✓ Strong consumer demand iPhones</div>
              <div className="sentiment-point">✓ Positive market reaction to product launches</div>
              <div className="sentiment-point">✓ Dynamics sustain moderate bullish sentiment</div>
              <div className="sentiment-point">✓ Minor impact on recent price movement</div>
            </div>
          </div>

          <div className="news-headlines">
            <h3>Top weighted headlines</h3>
            <div className="headline-item">
              <span className="sentiment-icon">😊</span>
              <span className="headline-text">Consumer demand for iPhone remains</span>
              <span className="headline-weight">1.2</span>
            </div>
          </div>
        </div>

        <div className="right-panel">
          <div className="sentiment-gauge-section">
            <h3>Sentiment Gauge</h3>
            <div className="gauge-container">
              <div className="gauge-circle">62</div>
              <div className="gauge-label">Moderately Bullish</div>
            </div>
            <div className="gauge-details">
              <div className="gauge-detail">Recent news suggests consumer demand for iPhone remains strong</div>
            </div>
          </div>

          <div className="current-metrics">
            <h3>Now</h3>
            <div className="metric-item">
              <span className="metric-icon">✓</span>
              <span className="metric-label">Volume</span>
              <span className="metric-info">ⓘ</span>
            </div>
            <div className="metric-item">
              <span className="metric-icon">~</span>
              <span className="metric-label">Volatility</span>
              <span className="metric-info">ⓘ</span>
            </div>
            <div className="metric-item">
              <span className="metric-icon">📈</span>
              <span className="metric-label">News velocity</span>
              <span className="metric-info">ⓘ</span>
            </div>
            <div className="metric-item">
              <span className="metric-icon">📰</span>
              <span className="metric-label">Headline count last hour</span>
              <span className="metric-info">ⓘ</span>
            </div>
          </div>

          <div className="top-headlines">
            <h3>Top weighted headlines</h3>
            <div className="headline-item">
              <span className="sentiment-icon">✓</span>
              <span className="headline-text">Consumer demand for iPhone remains</span>
              <span className="headline-weight">1.2</span>
            </div>
            <div className="headline-item">
              <span className="sentiment-icon">😊</span>
              <span className="headline-text">Investors positive on smartphone market</span>
              <span className="headline-weight">0.4</span>
            </div>
          </div>

          <div className="update-timer">
            Next update in 48m 30s
          </div>
        </div>
      </div>

      <div className="bottom-panel">
        <div className="news-feed">
          <h3>News Feed</h3>
          <div className="news-item">
            <div className="news-icon">📰</div>
            <div className="news-content">
              <div className="news-title">Tech Giant Unveils New Product Lineup</div>
              <div className="news-sentiment">Positive</div>
            </div>
          </div>
          <div className="news-item">
            <div className="news-icon">📰</div>
            <div className="news-content">
              <div className="news-title">Market Awaits Federal Reserve Decision</div>
              <div className="news-sentiment">Neutral</div>
            </div>
          </div>
          <div className="news-item">
            <div className="news-icon">📰</div>
            <div className="news-content">
              <div className="news-title">Supply Chain Issues Impacting Production</div>
              <div className="news-sentiment">Negative</div>
            </div>
          </div>
        </div>

        <div className="market-overview">
          <h3>Market Overview</h3>
          <div className="market-item">
            <div className="ticker">AAPL</div>
            <div className="price">155.84</div>
            <div className="change">-0.56%</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="market-item">
            <div className="ticker">TSLA</div>
            <div className="price">141.69</div>
            <div className="change">+0.5%</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="market-item">
            <div className="ticker">AMZN</div>
            <div className="price">180.40</div>
            <div className="change">+0.72%</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="market-item">
            <div className="ticker">GOOGL</div>
            <div className="price">154.76</div>
            <div className="change">156.74</div>
            <div className="mini-chart">📈</div>
          </div>
        </div>

        <div className="predictions">
          <h3>Prediction</h3>
          <div className="prediction-item">
            <div className="ticker">AAPL</div>
            <div className="prediction-range">165.85 - 169.63</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="prediction-item">
            <div className="ticker">TSLA</div>
            <div className="prediction-value">145</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="prediction-item">
            <div className="ticker">AMZN</div>
            <div className="prediction-value">180</div>
            <div className="mini-chart">📈</div>
          </div>
          <div className="prediction-item">
            <div className="ticker">GOOGL</div>
            <div className="prediction-value">154.76</div>
            <div className="mini-chart">📈</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

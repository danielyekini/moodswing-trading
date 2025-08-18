import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-page">
      <div className="navbar">
        <div className="navbar-brand"></div>
        <div className="navbar-nav">
          <div className="nav-item active"></div>
          <div className="nav-item"></div>
          <div className="nav-item"></div>
          <div className="nav-item"></div>
        </div>
        <div className="navbar-actions">
          <div className="search-box"></div>
          <div className="user-profile"></div>
        </div>
      </div>

      <div className="dashboard-content">
        <div className="left-panel">
          <div className="stock-price-section">
            <div className="stock-symbol"></div>
            <div className="stock-price"></div>
            <div className="stock-change"></div>
          </div>

          <div className="main-chart">
            <div className="chart-placeholder"></div>
          </div>

          <div className="sentiment-analysis">
            <div className="section-title"></div>
            <div className="sentiment-points">
              <div className="sentiment-point"></div>
              <div className="sentiment-point"></div>
              <div className="sentiment-point"></div>
              <div className="sentiment-point"></div>
            </div>
          </div>

          <div className="news-headlines">
            <div className="section-title"></div>
            <div className="headline-item">
              <div className="sentiment-icon"></div>
              <div className="headline-text"></div>
              <div className="headline-weight"></div>
            </div>
          </div>
        </div>

        <div className="right-panel">
          <div className="sentiment-gauge-section">
            <div className="section-title"></div>
            <div className="gauge-container">
              <div className="gauge-circle"></div>
              <div className="gauge-label"></div>
            </div>
            <div className="gauge-details">
              <div className="gauge-detail"></div>
            </div>
          </div>

          <div className="current-metrics">
            <div className="section-title"></div>
            <div className="metric-item">
              <div className="metric-icon"></div>
              <div className="metric-label"></div>
              <div className="metric-info"></div>
            </div>
            <div className="metric-item">
              <div className="metric-icon"></div>
              <div className="metric-label"></div>
              <div className="metric-info"></div>
            </div>
            <div className="metric-item">
              <div className="metric-icon"></div>
              <div className="metric-label"></div>
              <div className="metric-info"></div>
            </div>
            <div className="metric-item">
              <div className="metric-icon"></div>
              <div className="metric-label"></div>
              <div className="metric-info"></div>
            </div>
          </div>

          <div className="top-headlines">
            <div className="section-title"></div>
            <div className="headline-item">
              <div className="sentiment-icon"></div>
              <div className="headline-text"></div>
              <div className="headline-weight"></div>
            </div>
            <div className="headline-item">
              <div className="sentiment-icon"></div>
              <div className="headline-text"></div>
              <div className="headline-weight"></div>
            </div>
          </div>

          <div className="update-timer"></div>
        </div>
      </div>

      <div className="bottom-panel">
        <div className="news-feed">
          <div className="section-title"></div>
          <div className="news-item">
            <div className="news-icon"></div>
            <div className="news-content">
              <div className="news-title"></div>
              <div className="news-sentiment"></div>
            </div>
          </div>
          <div className="news-item">
            <div className="news-icon"></div>
            <div className="news-content">
              <div className="news-title"></div>
              <div className="news-sentiment"></div>
            </div>
          </div>
          <div className="news-item">
            <div className="news-icon"></div>
            <div className="news-content">
              <div className="news-title"></div>
              <div className="news-sentiment"></div>
            </div>
          </div>
        </div>

        <div className="market-overview">
          <div className="section-title"></div>
          <div className="market-item">
            <div className="ticker"></div>
            <div className="price"></div>
            <div className="change"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="market-item">
            <div className="ticker"></div>
            <div className="price"></div>
            <div className="change"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="market-item">
            <div className="ticker"></div>
            <div className="price"></div>
            <div className="change"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="market-item">
            <div className="ticker"></div>
            <div className="price"></div>
            <div className="change"></div>
            <div className="mini-chart"></div>
          </div>
        </div>

        <div className="predictions">
          <div className="section-title"></div>
          <div className="prediction-item">
            <div className="ticker"></div>
            <div className="prediction-range"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="prediction-item">
            <div className="ticker"></div>
            <div className="prediction-value"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="prediction-item">
            <div className="ticker"></div>
            <div className="prediction-value"></div>
            <div className="mini-chart"></div>
          </div>
          <div className="prediction-item">
            <div className="ticker"></div>
            <div className="prediction-value"></div>
            <div className="mini-chart"></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

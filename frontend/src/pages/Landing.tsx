import React from 'react';

const Landing: React.FC = () => {
  return (
    <div className="landing-page">
      <div className="navbar">
        <div className="navbar-brand">MoodSwing Trading</div>
        <div className="navbar-nav">
          <div className="nav-item">Dashboard</div>
          <div className="nav-item">Explore</div>
          <div className="nav-item">API</div>
          <div className="nav-item">Status</div>
        </div>
        <div className="navbar-actions">
          <button className="btn-primary">Open Dashboard</button>
        </div>
      </div>

      <div className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">Trade the news as it lands</h1>
          <div className="hero-features">
            <div className="feature-item">5s WS ticks, alpha-blended MoodScore</div>
            <div className="feature-item">JSON logs and metrics</div>
          </div>
          <button className="hero-cta">Open Dashboard</button>
        </div>
        <div className="hero-visual">
          <div className="sentiment-gauge">62</div>
          <div className="mini-charts">
            <div className="mini-chart">AAPL</div>
            <div className="mini-chart">AAPL</div>
            <div className="mini-chart">AAPL</div>
            <div className="mini-chart">AMZN</div>
          </div>
        </div>
      </div>

      <div className="stats-section">
        <div className="stat-item">
          <div className="stat-number">24</div>
          <div className="stat-label">supported tickers</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">&lt;200ms</div>
          <div className="stat-label">115 p%</div>
        </div>
        <div className="stat-item">
          <div className="stat-number">60s</div>
          <div className="stat-label">news cache</div>
        </div>
      </div>

      <div className="how-it-works-section">
        <h2>How it works</h2>
        <div className="steps">
          <div className="step">
            <div className="step-number">1</div>
            <div className="step-title">Ingest</div>
            <div className="step-description">Pull and score headlines</div>
          </div>
          <div className="step">
            <div className="step-number">2</div>
            <div className="step-title">Aggregate</div>
            <div className="step-description">Compute MoodScore</div>
          </div>
          <div className="step">
            <div className="step-number">3</div>
            <div className="step-title">Predict</div>
            <div className="step-description">Forecast price trends</div>
          </div>
          <div className="step">
            <div className="step-number">4</div>
            <div className="step-title">Deliver</div>
            <div className="step-description">Push via WebSockets</div>
          </div>
        </div>
      </div>

      <div className="api-quickstart-section">
        <h2>API Quickstart</h2>
        <div className="api-tabs">
          <div className="api-tab">curl</div>
          <div className="api-tab">python</div>
          <div className="api-tab">websocket</div>
        </div>
        <div className="api-code">
          <code>
            1. curl --get/.moodswing.trading.account:deptboard/user1/
            2. get-/sentiment
          </code>
        </div>
      </div>

      <div className="whos-it-for-section">
        <h2>Who's it for?</h2>
        <div className="target-groups">
          <div className="target-group">
            <h3>Active Traders</h3>
            <p>Spot sentiment shifts</p>
          </div>
          <div className="target-group">
            <h3>Quantitative Analysts</h3>
            <p>Engineer custom signals</p>
          </div>
          <div className="target-group">
            <h3>Financial Developers</h3>
            <p>Build your own apps</p>
          </div>
        </div>
      </div>

      <div className="faq-section">
        <h2>FAQ</h2>
        <div className="faq-items">
          <div className="faq-item">
            <h3>What is MoodScore?</h3>
            <p>What is MoodScore?</p>
          </div>
          <div className="faq-item">
            <h3>Which assets are tracked</h3>
            <p>Engineer custom signals</p>
          </div>
        </div>
      </div>

      <div className="ready-section">
        <h2>Ready to see it live?</h2>
        <button className="btn-primary">Open Dashboard</button>
      </div>

      <div className="footer">
        <div className="footer-links">
          <div className="footer-link">Methodology</div>
          <div className="footer-link">Legal</div>
          <div className="footer-link">Status</div>
        </div>
      </div>
    </div>
  );
};

export default Landing;

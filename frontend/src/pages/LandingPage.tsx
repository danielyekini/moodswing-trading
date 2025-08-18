import './LandingPage.css'

function LandingPage() {
  return (
    <div className="landing-page">
      {/* Navigation Bar */}
      <div className="placeholder-div navbar" data-name="Navbar">
        <span>Navigation Bar - Logo, Menu Items, Open Dashboard Button</span>
      </div>

      {/* Hero Section */}
      <div className="placeholder-div hero-section" data-name="Hero">
        <span>Hero Section - Main Headline, Subtext, CTA Button, MoodScore Widget</span>
      </div>

      {/* Stats Section */}
      <div className="placeholder-div stats-section" data-name="Stats">
        <span>Stats Section - Key Metrics (24 supported tickers, &lt;200ms, 60s news cache)</span>
      </div>

      {/* How It Works Section */}
      <div className="placeholder-div how-it-works" data-name="How It Works">
        <span>How It Works - 4 Step Process (Ingest, Aggregate, Predict, Deliver)</span>
      </div>

      {/* API Quickstart Section */}
      <div className="placeholder-div api-quickstart" data-name="API Quickstart">
        <span>API Quickstart - Code Examples with curl, python, websocket tabs</span>
      </div>

      {/* Target Audience Section */}
      <div className="placeholder-div target-audience" data-name="Target Audience">
        <span>Who's It For - Active Traders, Quantitative Analysts, Financial Developers</span>
      </div>

      {/* FAQ Section */}
      <div className="placeholder-div faq-section" data-name="FAQ">
        <span>FAQ Section - Common Questions and Answers</span>
      </div>

      {/* Footer CTA */}
      <div className="placeholder-div footer-cta" data-name="Footer CTA">
        <span>Ready to See It Live? - Final CTA with Open Dashboard Button</span>
      </div>

      {/* Footer */}
      <div className="placeholder-div footer" data-name="Footer">
        <span>Footer - Links (Methodology, Legal, Status)</span>
      </div>
    </div>
  )
}

export default LandingPage

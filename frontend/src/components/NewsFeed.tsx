import { useEffect, useState } from 'react'
import './NewsFeed.css'

interface NewsArticle {
  id: string
  headline: string
  source: string
  url: string
  ts_pub: string
  sentiment: number // -1 to 1 scale
  weight: number
  image_url?: string // Optional image URL
}

interface NewsFeedProps {
  ticker: string
}

function NewsFeed({ ticker }: NewsFeedProps) {
  const [articles, setArticles] = useState<NewsArticle[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Helper function to get sentiment label and color
  const getSentimentInfo = (sentiment: number) => {
    if (sentiment > 0.3) {
      return { label: 'Positive', color: '#10B981', bgColor: 'rgba(16, 185, 129, 0.1)' }
    } else if (sentiment < -0.3) {
      return { label: 'Negative', color: '#EF4444', bgColor: 'rgba(239, 68, 68, 0.1)' }
    } else {
      return { label: 'Neutral', color: '#6B7280', bgColor: 'rgba(107, 114, 128, 0.1)' }
    }
  }

  // Helper function to format time
  const formatTime = (isoString: string) => {
    const date = new Date(isoString)
    const now = new Date()
    const diffMs = now.getTime() - date.getTime()
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
    const diffMinutes = Math.floor(diffMs / (1000 * 60))
    
    if (diffHours >= 24) {
      const diffDays = Math.floor(diffHours / 24)
      return `${diffDays}d ago`
    } else if (diffHours >= 1) {
      return `${diffHours}h ago`
    } else if (diffMinutes >= 1) {
      return `${diffMinutes}m ago`
    } else {
      return 'Just now'
    }
  }

  // Fetch news articles on mount
  useEffect(() => {
    const fetchNews = async () => {
      try {
        setLoading(true)
        setError(null)
        
        console.log(`Fetching news for ticker: ${ticker}`)
        const response = await fetch(`http://127.0.0.1:8000/api/v1/news/${ticker}?limit=10`, {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        })
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`)
        }
        
        const data = await response.json()
        console.log('News data:', data)
        
        if (data.articles && Array.isArray(data.articles) && data.articles.length > 0) {
          // Map the API response to our interface format
          const mappedArticles: NewsArticle[] = data.articles.map((article: any, index: number) => ({
            id: article.id || `article-${index}`,
            headline: article.headline || 'No headline available',
            source: article.source || article.provider || 'Unknown',
            url: article.url || '#',
            ts_pub: article.ts_pub || new Date().toISOString(),
            sentiment: typeof article.sentiment === 'number' ? article.sentiment : 0,
            weight: typeof article.weight === 'number' ? article.weight : 1,
            image_url: article.image_url
          }))
          setArticles(mappedArticles)
          console.log(`Loaded ${mappedArticles.length} articles from API`)
        } else {
          console.log('No articles in API response, using dummy data')
          // Fallback to dummy data when no articles available
          setArticles(dummyArticles)
        }
      } catch (error) {
        console.error('Failed to fetch news:', error)
        setError('Failed to load news')
        // Use dummy data as fallback when API fails
        setArticles(dummyArticles)
      } finally {
        setLoading(false)
      }
    }

    fetchNews()
  }, [ticker])

  // Helper function to get icon placeholder based on article type/source
  const getIconPlaceholder = (source: string, index: number) => {
    const icons = [
      { icon: '📱', color: '#3B82F6' }, // Tech
      { icon: '💼', color: '#10B981' }, // Business
      { icon: '🏭', color: '#F59E0B' }, // Industry
      { icon: '📈', color: '#8B5CF6' }, // Finance
      { icon: '⚖️', color: '#EF4444' }  // Legal/Regulatory
    ]
    
    // Select icon based on source or index
    let iconIndex = index % icons.length
    if (source.toLowerCase().includes('tech')) iconIndex = 0
    else if (source.toLowerCase().includes('bloomberg') || source.toLowerCase().includes('financial')) iconIndex = 3
    else if (source.toLowerCase().includes('cnbc')) iconIndex = 2
    
    return icons[iconIndex]
  }

  // Dummy data for development/fallback
  const dummyArticles: NewsArticle[] = [
    {
      id: '1',
      headline: 'Tech Giant Unveils New Product Lineup',
      source: 'Reuters',
      url: '#',
      ts_pub: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
      sentiment: 0.6,
      weight: 0.9
    },
    {
      id: '2',
      headline: 'Market Awaits Federal Reserve Decision',
      source: 'Bloomberg',
      url: '#',
      ts_pub: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(), // 4 hours ago
      sentiment: 0.1,
      weight: 0.8
    },
    {
      id: '3',
      headline: 'Supply Chain Issues Impacting Production',
      source: 'CNBC',
      url: '#',
      ts_pub: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(), // 6 hours ago
      sentiment: -0.5,
      weight: 0.7
    },
    {
      id: '4',
      headline: 'Q4 Earnings Beat Expectations Across Sector',
      source: 'Financial Times',
      url: '#',
      ts_pub: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(), // 8 hours ago
      sentiment: 0.7,
      weight: 0.85
    },
    {
      id: '5',
      headline: 'Regulatory Changes May Affect Industry Growth',
      source: 'Wall Street Journal',
      url: '#',
      ts_pub: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(), // 12 hours ago
      sentiment: -0.2,
      weight: 0.6
    }
  ]

  if (loading) {
    return (
      <div className="card news-feed">
        <div className="news-header">
          <h3>News Feed</h3>
        </div>
        <div className="news-loading">
          <div className="loading-spinner"></div>
          <span>Loading news...</span>
        </div>
      </div>
    )
  }

  if (error && articles.length === 0) {
    return (
      <div className="card news-feed">
        <div className="news-header">
          <h3>News Feed</h3>
        </div>
        <div className="news-error">
          <span>Unable to load news articles</span>
        </div>
      </div>
    )
  }

  return (
    <div className="card news-feed">
      <div className="news-header">
        <h3>News Feed</h3>
        <span className="news-ticker">{ticker}</span>
      </div>
      
      <div className="news-articles">
        {articles.map((article, index) => {
          const sentimentInfo = getSentimentInfo(article.sentiment)
          const iconPlaceholder = getIconPlaceholder(article.source, index)
          
          return (
            <div key={article.id} className="news-article">
              <a 
                href={article.url} 
                target="_blank" 
                rel="noopener noreferrer"
                className="article-link"
              >
                <div className="article-content">
                  {/* Article Icon/Image */}
                  <div className="article-image">
                    {article.image_url ? (
                      <img 
                        src={article.image_url} 
                        alt={article.headline}
                        onError={(e) => {
                          // Hide the img and show icon fallback
                          const target = e.target as HTMLImageElement
                          target.style.display = 'none'
                          const iconDiv = target.nextElementSibling as HTMLElement
                          if (iconDiv) iconDiv.style.display = 'flex'
                        }}
                      />
                    ) : null}
                    <div 
                      className="article-icon-placeholder"
                      style={{ 
                        backgroundColor: iconPlaceholder.color,
                        display: article.image_url ? 'none' : 'flex'
                      }}
                    >
                      <span className="article-icon">{iconPlaceholder.icon}</span>
                    </div>
                  </div>
                  
                  {/* Article Text Content */}
                  <div className="article-text">
                    <div className="article-header">
                      <span className="article-time">{formatTime(article.ts_pub)}</span>
                      <div 
                        className="sentiment-badge"
                        style={{ 
                          color: sentimentInfo.color, 
                          backgroundColor: sentimentInfo.bgColor 
                        }}
                      >
                        {sentimentInfo.label}
                      </div>
                    </div>
                    
                    <h4 className="article-headline">
                      {article.headline}
                    </h4>
                    
                    <div className="article-footer">
                      <span className="article-source">{article.source}</span>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          )
        })}
      </div>
      
      {articles.length === 0 && (
        <div className="news-empty">
          <span>No news articles available</span>
        </div>
      )}
    </div>
  )
}

export default NewsFeed

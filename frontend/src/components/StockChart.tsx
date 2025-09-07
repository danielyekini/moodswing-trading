import { useEffect, useState, useRef } from 'react'
import Highcharts from 'highcharts/highstock'
import './StockChart.css'

interface StockChartProps {
  ticker: string
}

function StockChart({ ticker }: StockChartProps) {
  const [chartType, setChartType] = useState<'ohlc' | 'line'>('ohlc')
  const [menuOpen, setMenuOpen] = useState(false)
  const [historicalData, setHistoricalData] = useState<[number, number, number, number, number][]>([])
  const [currentPrice, setCurrentPrice] = useState<number | null>(null)
  const [priceChange, setPriceChange] = useState<{ delta: number, percent: number } | null>(null)
  const [connectionStatus, setConnectionStatus] = useState<'connecting' | 'connected' | 'disconnected' | 'market-closed'>('disconnected')
  
  const wsRef = useRef<WebSocket | null>(null)
  const chartRef = useRef<Highcharts.Chart | null>(null)

  // Trading hours logic (US Eastern Time: 9:30 AM - 4:00 PM, Mon-Fri)
  const isMarketOpen = () => {
    const now = new Date()
    const et = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}))
    const dayOfWeek = et.getDay() // 0 = Sunday, 1 = Monday, ..., 6 = Saturday
    const hour = et.getHours()
    const minute = et.getMinutes()
    const timeInMinutes = hour * 60 + minute
    
    // Check if it's a weekday (Monday = 1, Friday = 5)
    if (dayOfWeek < 1 || dayOfWeek > 5) {
      return false
    }
    
    // Market open: 9:30 AM (570 minutes) to 4:00 PM (960 minutes) ET
    return timeInMinutes >= 570 && timeInMinutes < 960
  }

  const getMarketStatusMessage = () => {
    if (isMarketOpen()) {
      return connectionStatus === 'connected' ? 'Live data connected' : 'Connecting to live data...'
    } else {
      const now = new Date()
      const et = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}))
      const dayOfWeek = et.getDay()
      
      if (dayOfWeek === 0 || dayOfWeek === 6) {
        return 'Market closed - Weekend'
      } else {
        const hour = et.getHours()
        if (hour < 9 || (hour === 9 && et.getMinutes() < 30)) {
          return 'Market opens at 9:30 AM ET'
        } else {
          return 'Market closed at 4:00 PM ET'
        }
      }
    }
  }

  const chartData = historicalData
  const lastClose = currentPrice || (chartData.length > 0 ? chartData[chartData.length - 1][4] : 175)
  const prevClose = chartData.length > 1 ? chartData[chartData.length - 2][4] : lastClose
  const delta = priceChange?.delta || (lastClose - prevClose)
  const pctChange = priceChange?.percent || +(delta / prevClose * 100).toFixed(2)
  const isUp = delta >= 0

  // Fetch historical daily data on mount
  useEffect(() => {
    const fetchHistoricalData = async () => {
      try {
        const endDate = new Date().toISOString().split('T')[0]
        const startDate = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0] // 30 days ago
        
        const response = await fetch(
          `http://127.0.0.1:8000/api/v1/stocks/${ticker}/history?start=${startDate}&end=${endDate}&interval=1d`
        )
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`)
        }
        
        const data = await response.json()
        console.log('Historical data:', data)
        
        if (data.candles && data.candles.length > 0) {
          // Convert candles to chart format: [timestamp, open, high, low, close]
          const chartCandles: [number, number, number, number, number][] = data.candles.map((candle: any) => [
            new Date(candle.ts).getTime(),
            candle.open,
            candle.high,
            candle.low,
            candle.close
          ])
          
          setHistoricalData(chartCandles)
          console.log('Set historical data:', chartCandles.length, 'candles')
        }
      } catch (error) {
        console.error('Failed to fetch historical data:', error)
        // Fallback to dummy data
        const fallbackData: [number, number, number, number, number][] = [
          [Date.UTC(2024, 11, 2), 175.0, 176.2, 174.6, 175.4],
          [Date.UTC(2024, 11, 3), 175.4, 176.8, 174.9, 176.1],
          [Date.UTC(2024, 11, 4), 176.1, 177.3, 175.2, 176.9],
          [Date.UTC(2024, 11, 5), 176.9, 178.0, 176.5, 177.7],
          [Date.UTC(2024, 11, 6), 177.7, 178.6, 176.8, 177.2],
        ]
        setHistoricalData(fallbackData)
      }
    }

    fetchHistoricalData()
  }, [ticker])

  // WebSocket connection for live data
  useEffect(() => {
    const connectWebSocket = () => {
      // Only connect during market hours
      if (!isMarketOpen()) {
        setConnectionStatus('market-closed')
        console.log('Market is closed, not connecting to WebSocket')
        return
      }

      if (wsRef.current?.readyState === WebSocket.OPEN) return

      setConnectionStatus('connecting')
      const ws = new WebSocket(`ws://127.0.0.1:8000/api/v1/stocks/${ticker}/stream?interval=5`)
      wsRef.current = ws

      ws.onopen = () => {
        setConnectionStatus('connected')
        console.log('WebSocket connected')
      }

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data)
          console.log('WebSocket message:', data) // Debug log
          
          if (data.type === 'ping') {
            ws.send(JSON.stringify({ type: 'pong' }))
            return
          }
          
          if (data.type === 'rate') {
            // Rate limiting info, can be used for UI feedback
            return
          }

          // Handle tick data
          if (data.price && data.ts) {
            const timestamp = new Date(data.ts).getTime()
            const price = parseFloat(data.price)
            
            setCurrentPrice(price)
            
            // Calculate price change from last historical close
            if (chartData.length > 0) {
              const lastHistoricalClose = chartData[chartData.length - 1][4]
              const delta = price - lastHistoricalClose
              const percent = (delta / lastHistoricalClose) * 100
              setPriceChange({ delta, percent })
            }
            
            // Add live tick to chart using addPoint (more efficient than recreating series)
            if (chartRef.current) {
              const series = chartRef.current.series[0]
              if (series) {
                if (chartType === 'line') {
                  // Add point to line series
                  series.addPoint([timestamp, price], true, false)
                } else {
                  // For OHLC, use current price for all values (simplified live tick)
                  series.addPoint([timestamp, price, price, price, price], true, false)
                }
              }
            }
          }
        } catch (error) {
          console.error('WebSocket message error:', error)
        }
      }

      ws.onerror = (error) => {
        console.error('WebSocket error:', error)
        setConnectionStatus('disconnected')
      }

      ws.onclose = () => {
        setConnectionStatus('disconnected')
        console.log('WebSocket disconnected')
        // Reconnect after 5 seconds only if market is still open
        setTimeout(() => {
          if (isMarketOpen()) {
            connectWebSocket()
          } else {
            setConnectionStatus('market-closed')
          }
        }, 5000)
      }
    }

    // Initial connection attempt
    connectWebSocket()

    // Set up boundary timers for market open/close times
    const now = new Date()
    const et = new Date(now.toLocaleString("en-US", {timeZone: "America/New_York"}))
    const dayOfWeek = et.getDay()
    
    const timeouts: number[] = []
    
    // Only set timers for weekdays
    if (dayOfWeek >= 1 && dayOfWeek <= 5) {
      // Calculate time until market open (9:30 AM ET)
      const marketOpen = new Date(et)
      marketOpen.setHours(9, 30, 0, 0)
      if (marketOpen <= et) {
        // If past 9:30 today, set for tomorrow
        marketOpen.setDate(marketOpen.getDate() + 1)
      }
      
      // Calculate time until market close (4:00 PM ET)
      const marketClose = new Date(et)
      marketClose.setHours(16, 0, 0, 0)
      if (marketClose <= et) {
        // If past 4:00 today, set for tomorrow
        marketClose.setDate(marketClose.getDate() + 1)
      }
      
      // Timer for market open
      const msUntilOpen = marketOpen.getTime() - et.getTime()
      if (msUntilOpen > 0) {
        timeouts.push(setTimeout(() => {
          console.log('Market opened, connecting to WebSocket')
          connectWebSocket()
        }, msUntilOpen))
      }
      
      // Timer for market close
      const msUntilClose = marketClose.getTime() - et.getTime()
      if (msUntilClose > 0 && isMarketOpen()) {
        timeouts.push(setTimeout(() => {
          console.log('Market closed, disconnecting WebSocket')
          if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.close()
          }
          setConnectionStatus('market-closed')
        }, msUntilClose))
      }
    }

    return () => {
      timeouts.forEach(timeout => clearTimeout(timeout))
      if (wsRef.current) {
        wsRef.current.close()
      }
    }
  }, [ticker])

  // Initialize the primary stock chart after mount and when type changes
  useEffect(() => {
    // Don't create chart if no data yet
    if (chartData.length === 0) {
      console.log('Waiting for historical data...')
      return
    }

    const containerId = 'primary-stock-chart'
    const lineData: [number, number][] = chartData.map(([t, , , , c]) => [t, c])

    const seriesType: 'ohlc' | 'areaspline' = chartType === 'ohlc' ? 'ohlc' : 'areaspline'

    console.log('Creating chart with', chartData.length, 'data points')

    const chart = Highcharts.stockChart(containerId, {
      chart: {
        backgroundColor: 'transparent',
        style: { fontFamily: 'system-ui, -apple-system, Segoe UI, sans-serif' },
        spacing: [32, 16, 8, 8]
      },
      title: { text: '' },
      rangeSelector: { enabled: false },
      navigator: { enabled: false },
      scrollbar: { enabled: false },
      credits: { enabled: false },
      xAxis: {
        gridLineWidth: 0,
        minorGridLineWidth: 0,
        lineWidth: 0,
        tickLength: 0,
        labels: { style: { color: '#9CA3AF', fontSize: '12px' } },
        crosshair: { color: 'rgba(148, 163, 184, 0.12)' },
        maxPadding: 0.06
      },
      yAxis: {
        gridLineWidth: 0,
        minorGridLineWidth: 0,
        lineWidth: 0,
        tickLength: 0,
        labels: { style: { color: '#9CA3AF', fontSize: '12px' } },
        opposite: true,
        offset: 16
      },
      legend: { enabled: false },
      plotOptions: {
        series: {
          states: { hover: { enabled: false } },
          pointRange: 24 * 3600 * 1000
        },
        ohlc: { color: '#EF4444', upColor: '#10B981' },
        areaspline: {
          color: '#22D3EE',
          lineWidth: 2,
          marker: { enabled: false },
          fillColor: {
            linearGradient: { x1: 0, y1: 0, x2: 0, y2: 1 },
            stops: [
              [0, 'rgba(34, 211, 238, 0.35)'],
              [1, 'rgba(34, 211, 238, 0.00)']
            ]
          }
        }
      },
      tooltip: {
        backgroundColor: '#0B1220',
        borderColor: '#1F2937',
        borderRadius: 8,
        style: { color: '#E5E7EB' },
        shadow: false,
        valueDecimals: 2
      },
      series: [
        chartType === 'ohlc'
          ? {
              type: seriesType,
              name: ticker,
              data: chartData
            }
          : {
              type: seriesType,
              name: ticker,
              data: lineData,
              threshold: null
            }
      ] as any
    })

    chartRef.current = chart

    return () => {
      chart && chart.destroy()
    }
  }, [chartType, chartData])

  return (
    <div className="card primary-chart" style={{ position: 'relative' }}>
      <div style={{ position: 'absolute', left: 20, top: 16, zIndex: 2 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
          <span style={{ color: '#FFFFFF', fontSize: 28, fontWeight: 500 }}>{ticker}</span>
          <div 
            style={{ 
              width: 8, 
              height: 8, 
              borderRadius: '50%', 
              backgroundColor: 
                connectionStatus === 'connected' ? '#10B981' : 
                connectionStatus === 'connecting' ? '#F59E0B' : 
                connectionStatus === 'market-closed' ? '#EF4444' : 
                '#EF4444' 
            }}
            title={getMarketStatusMessage()}
          />
        </div>
        <div style={{ color: '#FFFFFF', fontSize: 56, fontWeight: 600, lineHeight: 1, marginBottom: 8 }}>
          {lastClose.toFixed(2)}
        </div>
        <div style={{ color: isUp ? '#10B981' : '#EF4444', fontSize: 14, fontWeight: 600 }}>
          Today {isUp ? '+' : ''}{pctChange.toFixed(2)}%
          {currentPrice && (
            <span style={{ marginLeft: 8, opacity: 0.7 }}>Live</span>
          )}
        </div>
      </div>
      <div style={{ position: 'absolute', right: 20, top: 16, zIndex: 3 }}>
        <div style={{ position: 'relative' }}>
          <button
            onClick={() => setMenuOpen(!menuOpen)}
            style={{
              padding: '6px 10px',
              backgroundColor: '#1F2937',
              color: '#FFFFFF',
              border: '1px solid #374151',
              borderRadius: 8,
              cursor: 'pointer',
              fontSize: 12
            }}
          >
            Chart Type ▾
          </button>
          {menuOpen && (
            <div
              style={{
                position: 'absolute',
                right: 0,
                marginTop: 6,
                backgroundColor: '#0B1220',
                border: '1px solid #374151',
                borderRadius: 8,
                padding: 10,
                minWidth: 160,
                boxShadow: '0 10px 24px rgba(0,0,0,0.35)'
              }}
            >
              <div style={{ color: '#9CA3AF', fontSize: 11, marginBottom: 6, textTransform: 'uppercase', letterSpacing: 0.6 }}>Display</div>
              <div>
                <button
                  onClick={() => { setChartType('line'); setMenuOpen(false) }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '6px 8px',
                    background: 'transparent',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: 6,
                    cursor: 'pointer',
                    fontSize: 12,
                    outline: 'none'
                  }}
                >
                  Line
                </button>
                <button
                  onClick={() => { setChartType('ohlc'); setMenuOpen(false) }}
                  style={{
                    width: '100%',
                    textAlign: 'left',
                    padding: '6px 8px',
                    background: 'transparent',
                    color: '#FFFFFF',
                    border: 'none',
                    borderRadius: 6,
                    cursor: 'pointer',
                    fontSize: 12,
                    outline: 'none'
                  }}
                >
                  OHLC
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      <div id="primary-stock-chart" style={{ width: '100%', height: 410 }} />
    </div>
  )
}

export default StockChart
'use client'

import { useState, useCallback } from 'react'
import axios from 'axios'
import { BIResponse, StockData, NewsData, Sentiment, Recommendation } from '../types/api'
import StockChart from '../components/StockChart'

export default function Home() {
  const [ticker, setTicker] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [data, setData] = useState<BIResponse | null>(null)

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

  const handleAnalyze = useCallback(async () => {
    if (!ticker.trim()) {
      setError('Please enter a ticker symbol (e.g., AAPL)')
      return
    }

    setError('')
    setLoading(true)
    setData(null)

    try {
      const response = await axios.get(`${API_URL}/api/bi?ticker=${ticker.toUpperCase()}`, {
        timeout: 30000, // 30s for FinBERT processing
      })

      if (response.data.status === 'success') {
        setData(response.data)
      } else {
        setError(response.data.error || 'Analysis failed')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Request failed. Ensure backend is running on port 8000.')
    } finally {
      setLoading(false)
    }
  }, [ticker, API_URL])

  return (
    <div className="container mx-auto px-4 py-12 max-w-7xl">
      <div className="text-center mb-16">
        <h1 className="text-5xl md:text-6xl font-bold bg-gradient-to-r from-primary-600 to-primary-700 bg-clip-text text-transparent mb-6">
          BI AI Engine
        </h1>
        <p className="text-xl text-gray-600 max-w-2xl mx-auto mb-12">
          AI-Powered stock analysis with FinBERT sentiment, market data, and business intelligence.
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 max-w-md mx-auto">
          <input
            type="text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value)}
            placeholder="Enter ticker (e.g., AAPL, MSFT)"
            className="flex-1 px-6 py-4 border border-gray-200 rounded-xl focus:ring-4 focus:ring-primary-500 focus:border-transparent text-lg shadow-sm"
            disabled={loading}
          />
          <button
            onClick={handleAnalyze}
            disabled={loading || !ticker.trim()}
            className="btn-primary px-8 py-4 text-lg font-semibold whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Analyzing...' : 'Analyze'}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-50 border border-red-200 rounded-xl text-red-800 font-medium">
            {error}
          </div>
        )}
      </div>

      {loading && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      )}

      {data && data.status === 'success' && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto">
          <StockChartSection data={data.data!.stock_data!} />
          <SentimentCardSection sentiment={data.data!.sentiment!} />
          <NewsFeedSection data={data.data!.news_data!} />
          <RecommendationsSection recommendations={data.data!.recommendations!} />
        </div>
      )}
    </div>
  )
}

function SkeletonCard() {
  return (
    <div className="card h-64">
      <div className="skeleton"></div>
      <div className="skeleton"></div>
      <div className="skeleton w-3/4"></div>
    </div>
  )
}

interface StockChartSectionProps {
  data: StockData
}

function StockChartSection({ data }: StockChartSectionProps) {
  return (
    <div className="md:col-span-2 lg:col-span-1 card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Stock Price (7d)</h2>
      <StockChart data={data} />

    </div>
  )
}

interface SentimentCardSectionProps {
  sentiment: Sentiment
}

function SentimentCardSection({ sentiment }: SentimentCardSectionProps) {
  const getColor = (score: number) => {
    if (score >= 7) return 'sentiment-positive'
    if (score >= 5) return 'sentiment-neutral'
    return 'sentiment-negative'
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Sentiment Score</h2>
      <div className="text-center">
        <div className={`text-5xl font-black mb-4 ${getColor(sentiment.score)}`}>
          {sentiment.score}
        </div>
        <div className="text-2xl font-semibold text-gray-700 mb-6">
          {sentiment.label}
        </div>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div 
            className={`h-4 rounded-full transition-all duration-1000 ${getColor(sentiment.score)}`}
            style={{ width: `${(sentiment.score / 10) * 100}%` }}
          ></div>
        </div>
        <p className="text-sm text-gray-500">
          FinBERT-powered analysis
        </p>
      </div>
    </div>
  )
}

interface NewsFeedSectionProps {
  data: NewsData
}

function NewsFeedSection({ data }: NewsFeedSectionProps) {
  return (
    <div className="lg:col-span-2 card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Latest News</h2>
      <div className="space-y-4 max-h-96 overflow-y-auto">
        {data.headlines.slice(0, 8).map((headline, idx) => (
          <div key={idx} className="p-4 border-l-4 border-primary-500 bg-gray-50 rounded-r-lg hover:bg-gray-100 transition-colors">
            <p className="text-gray-800 leading-relaxed">{headline}</p>
          </div>
        ))}
        {data.headlines.length === 0 && (
          <p className="text-gray-500 text-center py-12">No news available</p>
        )}
      </div>
      <p className="text-sm text-gray-500 mt-4">
        Source: {data.source} | {data.relevant_count} relevant headlines
      </p>
    </div>
  )
}

interface RecommendationsSectionProps {
  recommendations: Recommendation[]
}

function RecommendationsSection({ recommendations }: RecommendationsSectionProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'tinggi': return 'bg-red-100 border-red-300 text-red-800'
      case 'sedang': return 'bg-yellow-100 border-yellow-300 text-yellow-800'
      default: return 'bg-green-100 border-green-300 text-green-800'
    }
  }

  return (
    <div className="card">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">Recommendations</h2>
      <div className="space-y-4">
        {recommendations.map((rec, idx) => (
          <div key={idx} className={`p-5 border rounded-xl ${getPriorityColor(rec.priority)}`}>
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 w-2 h-2 rounded-full mt-2 bg-current opacity-75"></div>
              <div>
                <h3 className="font-bold text-lg mb-2">{rec.title}</h3>
                <p className="text-gray-700 leading-relaxed">{rec.description}</p>
                <span className="inline-block mt-3 px-3 py-1 bg-white/50 rounded-full text-xs font-semibold uppercase">
                  Priority: {rec.priority}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}


export interface StockData {
  dates: string[];
  closing_prices: number[];
  current_price: number | null;
  price_change: number;
  price_change_percent: number;
  average_price: number;
  highest_price: number | null;
  lowest_price: number | null;
}

export interface NewsData {
  source: string;
  headlines: string[];
  total_found: number;
  relevant_count: number;
}

export interface Sentiment {
  score: number;
  label: string;
  breakdown: {
    quantitative_score: number;
    finbert_score: number;
    positive_count?: number;
    negative_count?: number;
    neutral_count?: number;
  };
}

export interface Recommendation {
  title: string;
  description: string;
  priority: 'tinggi' | 'sedang' | 'rendah';
}

export interface BIResponse {
  status: 'success' | 'error';
  ticker: string;
  generated_at: string;
  data?: {
    stock_data: StockData;
    news_data: NewsData;
    sentiment: Sentiment;
    recommendations: Recommendation[];
  };
  error?: string;
}


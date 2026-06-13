'use client';

import { useEffect, useState } from 'react';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import MetricCards from '../components/MetricCards';
import SentimentBadge from '../components/SentimentBadge';
import PriceChart from '../components/PriceChart';
import NewsList from '../components/NewsList';
import RecommendationsList from '../components/RecommendationsList';
import TransparencyExplainability from '../components/TransparencyExplainability';
import { TrendingUp, TrendingDown } from 'lucide-react';
import { fetchAnalyze } from '@/lib/api';

export default function StockDataPage() {
  const [ticker] = useState('AAPL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [analysis, setAnalysis] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetchAnalyze(ticker);
        if (mounted) setAnalysis(res);
      } catch (e) {
        if (mounted) setError(e?.message ?? 'Unknown error');
        if (mounted) setAnalysis(null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [ticker]);

  const stock = analysis?.data?.stock_data;
  const sentiment = analysis?.data?.sentiment;
  const recommendations = analysis?.data?.recommendations;
  const headlines = analysis?.data?.news_data?.headlines;

  const currentPrice = stock?.current_price;
  const priceChange = stock?.price_change;
  const priceChangePercent = stock?.price_change_percent;

  const sentimentScore = sentiment?.score;
  const sentimentLabel = sentiment?.label;

  const isUp = typeof priceChangePercent === 'number' ? priceChangePercent >= 0 : false;

  const showHeader = !loading && !error && analysis?.ticker;

  return (
    <div className="mx-auto w-full max-w-6xl space-y-5 px-4 py-8">
      {loading ? (
        <LoadingSkeleton />
      ) : error ? (
        <ErrorState message={error} />
      ) : (
        analysis && (
          <div className="space-y-5">
            {showHeader && (
              <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                  <div className="min-w-0">
                    <div className="text-xs text-slate-300/70">Ticker</div>
                    <div className="mt-1 flex items-center gap-3">
                      <div className="text-3xl font-extrabold tracking-tight">{analysis?.ticker}</div>
                      <SentimentBadge label={sentimentLabel} score={sentimentScore} />
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="rounded-xl border border-white/10 bg-black/20 px-4 py-3">
                      <div className="text-xs text-slate-300/70">Trend</div>
                      <div className="mt-1 flex items-center gap-2 text-lg font-bold">
                        <span className={isUp ? 'text-emerald-300' : 'text-red-300'}>
                          {isUp ? <TrendingUp size={18} /> : <TrendingDown size={18} />}
                        </span>
                        {typeof priceChangePercent === 'number'
                          ? `${priceChangePercent >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%`
                          : '—'}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <MetricCards
              currentPrice={currentPrice}
              priceChange={priceChange}
              priceChangePercent={priceChangePercent}
              sentimentScore={sentimentScore}
            />

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
              <div className="lg:col-span-2">
                <PriceChart dates={stock?.dates} closingPrices={stock?.closing_prices} />
              </div>
              <div className="space-y-4">
                <NewsList headlines={headlines} />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-4 lg:grid-cols-3 lg:items-start">
              <div className="lg:col-span-2">
                <RecommendationsList recommendations={recommendations} />
              </div>
              <div className="lg:col-span-1">
                <TransparencyExplainability
                  analysis={analysis?.data?.analysis}
                  sentiment={sentiment}
                  newsData={analysis?.data?.news_data}
                  topPositiveDrivers={analysis?.data?.top_positive_drivers}
                  topNegativeDrivers={analysis?.data?.top_negative_drivers}
                />
              </div>
            </div>
          </div>
        )
      )}
    </div>
  );
}


 'use client';

import { useMemo, useState } from 'react';
import { TrendingUp, TrendingDown } from 'lucide-react';
import SearchBar from './components/SearchBar';
import LoadingSkeleton from './components/LoadingSkeleton';
import ErrorState from './components/ErrorState';
import MetricCards from './components/MetricCards';
import SentimentBadge from './components/SentimentBadge';
import PriceChart from './components/PriceChart';
import RecommendationsList from './components/RecommendationsList';
import NewsList from './components/NewsList';
import TransparencyExplainability from './components/TransparencyExplainability';
import IhsgDashboard from './components/IhsgDashboard';
import { fetchAnalyze, createRealtimeAnalyzeSocket, fetchIHsgDashboard } from '@/lib/api';

export default function Page() {
  const [ticker, setTicker] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [analysis, setAnalysis] = useState(null);

  const normalizedTicker = useMemo(() => ticker.trim().toUpperCase(), [ticker]);

  // realtime controls
  const [wsStatus, setWsStatus] = useState('idle');
  // Use function-scoped handles; cleanup is best-effort.
  let wsController = null;
  let intervalId = null;


  async function onAnalyze() {
    const t = normalizedTicker;
    setError(null);
    setLoading(true);
    setWsStatus('connecting');

    // cleanup previous run
    try {
      if (intervalId) clearInterval(intervalId);
      intervalId = null;
      if (wsController?.close) wsController.close();
      wsController = null;
    } catch {}

    try {
      // If WS fails for any reason, fallback to REST once
      wsController = createRealtimeAnalyzeSocket({
        ticker: t,
        onStatus: (s) => setWsStatus(s === 'connected' ? 'connected' : s === 'disconnected' ? 'disconnected' : s),
        onMessage: (data) => {
          setAnalysis(data);
          setLoading(false);
        },
        onError: async () => {
          // fallback REST
          try {
            const res = await fetchAnalyze(t);
            setAnalysis(res);
            setLoading(false);
          } catch (e) {
            setError(e?.message ?? 'Unknown error');
            setAnalysis(null);
            setLoading(false);
          }
        }
      });

      // auto refresh loop (client sends message again every N seconds)
      const N_SECONDS = 30; // pilih interval agar tidak membebani server
      intervalId = setInterval(() => {
        wsController?.sendTick?.();
      }, N_SECONDS * 1000);
    } catch (e) {
      setError(e?.message ?? 'Unknown error');
      setAnalysis(null);
      setLoading(false);
      setWsStatus('error');
    }
  }


  const stock = analysis?.data?.stock_data;
  const sentiment = analysis?.data?.sentiment;
  const recommendations = analysis?.data?.recommendations;
  const headlines = analysis?.data?.news_data?.headlines;

  const currentPrice = stock?.current_price;
  const priceChange = stock?.price_change;
  const priceChangePercent = stock?.price_change_percent;

  const sentimentScore = sentiment?.score;
  const sentimentLabel = sentiment?.label;

  const showHeader = !loading && !error && analysis?.ticker;

  const isUp = typeof priceChangePercent === 'number' ? priceChangePercent >= 0 : false;

  return (
    <div className="mx-auto w-full max-w-6xl space-y-5 px-4 py-8">
      <div className="flex flex-col gap-2">
        <div className="flex items-center justify-between gap-3">
          <div>
            <div className="text-sm text-slate-300/70">BI AI Dashboard</div>
            <h1 className="text-2xl font-bold tracking-tight">Stock Sentiment & Recommendations</h1>
          </div>
          <div className="hidden rounded-2xl border border-white/10 bg-white/[0.03] px-4 py-3 sm:block">
            <div className="text-xs text-slate-300/70">Tip</div>
            <div className="mt-1 text-sm font-semibold">Try AAPL / BBCA</div>
          </div>
        </div>
      </div>

      <SearchBar
        ticker={ticker}
        onTickerChange={setTicker}
        onAnalyze={onAnalyze}
        disabled={loading || normalizedTicker.length === 0}
      />

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


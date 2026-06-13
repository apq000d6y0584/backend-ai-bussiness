'use client';

import { useEffect, useState } from 'react';
import SentimentBadge from '../components/SentimentBadge';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import { fetchAnalyze } from '@/lib/api';

export default function SentimentPage() {
  const [sentiment, setSentiment] = useState(null);
  const [ticker, setTicker] = useState('AAPL');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetchAnalyze(ticker);
        const s = res?.data?.sentiment;
        if (mounted) setSentiment(s);
      } catch (e) {
        if (mounted) setError(e?.message ?? 'Unknown error');
        if (mounted) setSentiment(null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, [ticker]);

  const score = sentiment?.score;
  const label = sentiment?.label;

  return (
    <div className="mx-auto w-full max-w-6xl space-y-5 px-4 py-8">
      {loading ? (
        <LoadingSkeleton />
      ) : error ? (
        <ErrorState message={error} />
      ) : (
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5">
          <div className="text-xs text-slate-300/70">Sentiment</div>
          <div className="mt-2 flex items-center gap-3">
            <div className="text-2xl font-extrabold tracking-tight">{ticker}</div>
            <SentimentBadge label={label} score={score} />
          </div>
          <div className="mt-3 text-sm text-slate-200/80">
            {typeof score === 'number' ? `Score: ${score.toFixed(2)}` : '—'}
          </div>
        </div>
      )}
    </div>
  );
}


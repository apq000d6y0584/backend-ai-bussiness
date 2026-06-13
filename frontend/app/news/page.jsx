'use client';

import { useEffect, useState } from 'react';
import NewsList from '../components/NewsList';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import { fetchAnalyze } from '@/lib/api';

export default function NewsPage() {
  const [headlines, setHeadlines] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetchAnalyze('AAPL');
        const hs = res?.data?.news_data?.headlines;
        if (mounted) setHeadlines(hs);
      } catch (e) {
        if (mounted) setError(e?.message ?? 'Unknown error');
        if (mounted) setHeadlines(null);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="mx-auto w-full max-w-6xl space-y-5 px-4 py-8">
      {loading ? (
        <LoadingSkeleton />
      ) : error ? (
        <ErrorState message={error} />
      ) : (
        <NewsList headlines={headlines} />
      )}
    </div>
  );
}


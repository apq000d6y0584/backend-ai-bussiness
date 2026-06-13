'use client';

import { useEffect, useState } from 'react';
import IhsgDashboard from '../components/IhsgDashboard';
import LoadingSkeleton from '../components/LoadingSkeleton';
import ErrorState from '../components/ErrorState';
import { fetchIHsgDashboard } from '@/lib/api';

export default function IhsgDashboardPage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        setLoading(true);
        setError(null);
        const res = await fetchIHsgDashboard();
        if (mounted) setData(res);
      } catch (e) {
        if (mounted) setError(e?.message ?? 'Unknown error');
        if (mounted) setData(null);
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
        data && <IhsgDashboard data={data} />
      )}
    </div>
  );
}


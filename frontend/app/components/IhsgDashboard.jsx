import { useMemo } from 'react';

function CategorySection({ title, items, theme }) {
  const safeItems = Array.isArray(items) ? items : [];

  const color = theme === 'bad'
    ? { header: 'text-red-300', border: 'border-red-400/25', badge: 'bg-red-400/10 text-red-200' }
    : theme === 'good'
      ? { header: 'text-emerald-300', border: 'border-emerald-400/25', badge: 'bg-emerald-400/10 text-emerald-200' }
      : { header: 'text-brand/90', border: 'border-brand/25', badge: 'bg-brand/10 text-brand-200' };

  return (
    <div className={`rounded-xl border ${color.border} bg-white/[0.03] p-4`}>
      <div className={`text-sm font-semibold ${color.header}`}>{title}</div>

      <div className="mt-3 space-y-2">
        {safeItems.length === 0 ? (
          <div className="text-sm text-slate-300/70">Tidak ada data.</div>
        ) : (
          safeItems.map((it) => {
            const returnPct = typeof it.return_pct === 'number' ? it.return_pct : null;
            const sign = returnPct == null ? '' : (returnPct >= 0 ? '+' : '');
            const deltaColor = returnPct == null
              ? 'text-slate-200/70'
              : returnPct >= 0
                ? 'text-emerald-300'
                : 'text-red-300';

            return (
              <div key={it.ticker} className="flex items-center justify-between gap-3 rounded-lg border border-white/10 bg-black/10 px-3 py-2">
                <div className="min-w-0">
                  <div className="truncate font-semibold text-slate-100/95">{it.ticker}</div>
                  <div className={`text-xs ${deltaColor}`}>Return: {returnPct == null ? '—' : `${sign}${returnPct.toFixed(2)}%`}</div>
                </div>
                <div className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold ${color.badge}`}>Score {typeof it.score === 'number' ? it.score.toFixed(2) : '—'}</div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

export default function IhsgDashboard({ data }) {
  const categories = data?.categories || {};

  const normalized = useMemo(() => {
    // backend contract (best-effort): accept either snake_case keys or camelCase
    return {
      top_gainers: categories.top_gainers ?? categories.topGainers ?? [],
      top_losers: categories.top_losers ?? categories.topLosers ?? [],
      growth_stocks: categories.growth_stocks ?? categories.growthStocks ?? [],
      value_stocks: categories.value_stocks ?? categories.valueStocks ?? [],
      bullish_stocks: categories.bullish_stocks ?? categories.bullishStocks ?? [],
      bearish_stocks: categories.bearish_stocks ?? categories.bearishStocks ?? [],
      multibagger_stocks: categories.multibagger_stocks ?? categories.multibaggerStocks ?? [],
      bagholder_stocks: categories.bagholder_stocks ?? categories.bagholderStocks ?? [],
      value_trap_stocks: categories.value_trap_stocks ?? categories.valueTrapStocks ?? [],
      zombie_stocks: categories.zombie_stocks ?? categories.zombieStocks ?? [],
    };
  }, [categories]);

  return (
    <div className="space-y-4">
      <CategorySection title="Top Gainers (5)" items={normalized.top_gainers} theme="good" />
      <CategorySection title="Top Losers (5)" items={normalized.top_losers} theme="bad" />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategorySection title="Growth Stocks (proxy)" items={normalized.growth_stocks} theme="good" />
        <CategorySection title="Value Stocks (proxy)" items={normalized.value_stocks} theme="brand" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategorySection title="Bullish Stocks (proxy)" items={normalized.bullish_stocks} theme="good" />
        <CategorySection title="Bearish Stocks (proxy)" items={normalized.bearish_stocks} theme="bad" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategorySection title="Multibagger Stocks (proxy)" items={normalized.multibagger_stocks} theme="good" />
        <CategorySection title="Bagholder Stocks (proxy)" items={normalized.bagholder_stocks} theme="bad" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <CategorySection title="Value Trap Stocks (proxy)" items={normalized.value_trap_stocks} theme="brand" />
        <CategorySection title="Zombie Stocks (proxy)" items={normalized.zombie_stocks} theme="brand" />
      </div>
    </div>
  );
}


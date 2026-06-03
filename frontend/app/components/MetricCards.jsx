import clsx from 'clsx';

function formatNumber(n) {
  if (n === null || n === undefined || Number.isNaN(Number(n))) return '—';
  const num = Number(n);
  return num.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

export default function MetricCards({
  currentPrice,
  priceChange,
  priceChangePercent,
  sentimentScore
}) {
  const isUp = typeof priceChangePercent === 'number' ? priceChangePercent >= 0 : null;
  const changeColor =
    isUp === null ? 'text-slate-200' : isUp ? 'text-emerald-300' : 'text-red-300';
  const changeBg =
    isUp === null ? 'bg-white/5' : isUp ? 'bg-emerald-400/10' : 'bg-red-400/10';
  const changeBorder =
    isUp === null
      ? 'border-white/10'
      : isUp
        ? 'border-emerald-400/25'
        : 'border-red-400/25';

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <div className="text-sm text-slate-200/75">Current Price</div>
        <div className="mt-2 text-3xl font-bold tracking-tight">{formatNumber(currentPrice)}</div>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <div className="text-sm text-slate-200/75">Price Change</div>
        <div className="mt-2 flex items-baseline justify-between gap-3">
          <div className="text-2xl font-bold">{formatNumber(priceChange)}</div>
          <div className={clsx('rounded-xl border px-3 py-1 text-sm font-semibold', changeColor, changeBg, changeBorder)}>
            {typeof priceChangePercent === 'number'
              ? `${priceChangePercent >= 0 ? '+' : ''}${priceChangePercent.toFixed(2)}%`
              : '—'}
          </div>
        </div>
      </div>

      <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
        <div className="text-sm text-slate-200/75">Sentiment Score</div>
        <div className="mt-2 text-3xl font-bold tracking-tight">
          {typeof sentimentScore === 'number' ? sentimentScore.toFixed(1) : '—'}
        </div>
        <div className="mt-2 text-xs text-slate-200/70">1—10 (FinBERT)</div>
      </div>
    </div>
  );
}


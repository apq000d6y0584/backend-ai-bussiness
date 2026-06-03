import { Search } from 'lucide-react';

export default function SearchBar({
  ticker,
  onTickerChange,
  onAnalyze,
  disabled
}) {
  return (
    <div className="flex w-full flex-col gap-3 rounded-2xl border border-white/10 bg-white/[0.03] p-4 shadow-soft md:flex-row md:items-center md:justify-between">
      <div className="min-w-0">
        <div className="flex items-center gap-2">
          <span className="inline-flex h-9 w-9 items-center justify-center rounded-xl bg-brand/20 text-brand">
            <Search size={18} />
          </span>
          <div>
            <div className="text-sm text-slate-200/80">Ticker</div>
            <div className="text-lg font-semibold">Stock Analyzer</div>
          </div>
        </div>
      </div>

      <div className="flex w-full flex-col gap-2 md:max-w-xl md:flex-row md:items-center">
        <input
          value={ticker}
          onChange={(e) => onTickerChange(e.target.value)}
          placeholder="e.g. AAPL, BBCA"
          className="w-full flex-1 rounded-xl border border-white/10 bg-black/30 px-4 py-3 text-slate-100 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-brand/40"
        />
        <button
          type="button"
          onClick={onAnalyze}
          disabled={disabled}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand px-5 py-3 font-semibold text-white shadow-glow disabled:cursor-not-allowed disabled:opacity-60"
        >
          Analyze
        </button>
      </div>
    </div>
  );
}


export default function NewsList({ headlines }) {
  const items = Array.isArray(headlines) ? headlines : [];

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="text-sm text-slate-200/75">Market News</div>
      <div className="mt-1 text-lg font-semibold">Latest Headlines</div>

      <div className="mt-4 space-y-3">
        {items.length === 0 ? (
          <div className="text-sm text-slate-300/70">No news headlines available.</div>
        ) : (
          items.slice(0, 5).map((h, idx) => (
            <div key={idx} className="rounded-xl border border-white/10 bg-black/20 p-3">
              <div className="text-sm text-slate-200/90">{h}</div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}


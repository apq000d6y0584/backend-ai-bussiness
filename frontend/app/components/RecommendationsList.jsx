import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

function priorityColor(priority) {
  const p = (priority || '').toLowerCase();
  if (p === 'tinggi')
    return {
      bg: 'bg-emerald-400/10',
      text: 'text-emerald-300',
      border: 'border-emerald-400/25',
      icon: ArrowUpRight
    };
  if (p === 'sedang')
    return {
      bg: 'bg-brand/10',
      text: 'text-brand/90',
      border: 'border-brand/25',
      icon: ArrowUpRight
    };
  return {
    bg: 'bg-red-400/10',
    text: 'text-red-300',
    border: 'border-red-400/25',
    icon: ArrowDownRight
  };
}

export default function RecommendationsList({ recommendations }) {
  const items = Array.isArray(recommendations) ? recommendations : [];

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="text-sm text-slate-200/75">Recommendations</div>
      <div className="mt-1 text-lg font-semibold">Actionable Insights</div>

      <div className="mt-4 space-y-3">
        {items.length === 0 ? (
          <div className="text-sm text-slate-300/70">No recommendations available.</div>
        ) : (
          items.map((rec, idx) => {
            const c = priorityColor(rec.priority);
            const Icon = c.icon;

            return (
              <div key={idx} className={`rounded-xl border ${c.border} ${c.bg} p-3`}>
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span
                        className={`inline-flex items-center justify-center rounded-lg border border-white/10 bg-black/20 p-1 ${c.text}`}
                      >
                        <Icon size={14} />
                      </span>
                      <div className="truncate font-semibold">{rec.title ?? 'Untitled'}</div>
                    </div>
                    <div className="mt-2 line-clamp-3 text-sm text-slate-200/80">
                      {rec.description ?? '—'}
                    </div>
                  </div>
                  <div
                    className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold ${c.text} ${c.bg}`}
                  >
                    {(rec.priority ?? 'rendah').toString()}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}


import clsx from 'clsx';

function toColor(label) {
  const l = (label || '').toLowerCase();
  if (l.includes('positif'))
    return {
      bg: 'bg-emerald-400/10',
      text: 'text-emerald-300',
      border: 'border-emerald-400/25'
    };
  if (l.includes('negatif'))
    return {
      bg: 'bg-red-400/10',
      text: 'text-red-300',
      border: 'border-red-400/25'
    };
  return {
    bg: 'bg-slate-500/10',
    text: 'text-slate-200',
    border: 'border-slate-500/20'
  };
}

export default function SentimentBadge({ label, score }) {
  const c = toColor(label);

  const normalized = label ? label.replace(/_/g, ' ') : 'netral';
  const displayLabel = normalized
    .split(' ')
    .filter(Boolean)
    .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-semibold',
        c.bg,
        c.text,
        c.border
      )}
    >
      <span className="opacity-90">{displayLabel}</span>
      <span className="text-slate-100/70">•</span>
      <span className="tabular-nums">
        {typeof score === 'number' ? score.toFixed(1) : '—'}
      </span>
    </span>
  );
}


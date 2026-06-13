'use client';

import { useMemo, useState } from 'react';

const TABS = [
  { key: 'ihsg', label: 'IHSG Dashboard' },
  { key: 'stock', label: 'Stock' },
  { key: 'news', label: 'News' },
  { key: 'sentiment', label: 'Sentiment' },
  { key: 'recommendation', label: 'Recomendation' },
];

function TabButton({ label, active, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={
        'whitespace-nowrap rounded-full border px-4 py-2 text-sm transition ' +
        (active
          ? 'border-white/20 bg-white/[0.08] font-semibold text-white'
          : 'border-white/10 bg-black/10 text-slate-200/80 hover:bg-white/[0.05]')
      }
    >
      {label}
    </button>
  );
}

export default function NavbarTabs() {
  const [active, setActive] = useState('ihsg');

  const activeLabel = useMemo(() => {
    return TABS.find((t) => t.key === active)?.label ?? '';
  }, [active]);

  return (
    <header className="sticky top-0 z-50 border-b border-white/10 bg-[#06070c]/80 backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center gap-3 px-4 py-3">
        <div className="min-w-0">
          <div className="text-xs text-slate-300/70">BI AI Dashboard</div>
          <div className="truncate text-sm font-semibold tracking-tight">{activeLabel}</div>
        </div>

        <nav className="ml-auto flex flex-wrap justify-end gap-2">
          {TABS.map((t) => (
            <TabButton
              key={t.key}
              label={t.label}
              active={t.key === active}
              onClick={() => setActive(t.key)}
            />
          ))}
        </nav>
      </div>
    </header>
  );
}


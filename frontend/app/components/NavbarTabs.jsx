'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

const tabs = [
  { href: '/', label: 'Stock Data' },
  { href: '/ihsg-dashboard', label: 'IHSG Dashboard' },
  { href: '/news', label: 'News' },
  { href: '/sentiment', label: 'Sentiment' },
  { href: '/stock-data', label: 'Stock Data' }
];

export default function NavbarTabs() {
  const pathname = usePathname();

  // Normalize pathname for highlighting
  const activeHref =
    pathname === '/stock-data' ? '/stock-data' : pathname === '/' ? '/' : pathname;

  return (
    <nav aria-label="Primary" className="sticky top-0 z-20">
      <div className="mx-auto w-full max-w-6xl px-4 py-3">
        <div className="rounded-2xl border border-white/10 bg-white/[0.03] px-3 py-2 backdrop-blur">
          <div className="flex flex-wrap items-center gap-2">
            <NavPills activeHref={activeHref} />
          </div>
        </div>
      </div>
    </nav>
  );
}

function NavPills({ activeHref }) {
  // Render exact menu requested: IHSG dashboard, news, sentiment, stock data
  const menu = [
    { href: '/ihsg-dashboard', label: 'IHSG dashboard' },
    { href: '/news', label: 'news' },
    { href: '/sentiment', label: 'sentiment' },
    { href: '/stock-data', label: 'stock data' }
  ];

  return (
    <>
      {menu.map((t) => {
        const active = activeHref === t.href || (t.href === '/stock-data' && activeHref === '/');
        return (
          <Link
            key={t.href}
            href={t.href}
            className={
              active
                ? 'rounded-xl bg-white/[0.08] px-3 py-2 text-sm font-semibold text-white'
                : 'rounded-xl px-3 py-2 text-sm font-semibold text-slate-200/80 hover:bg-white/[0.05] hover:text-white'
            }
          >
            {t.label}
          </Link>
        );
      })}
    </>
  );
}


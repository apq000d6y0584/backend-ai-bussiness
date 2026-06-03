import { AlertTriangle, Sparkles } from 'lucide-react';

function scoreColor(score) {
  if (score >= 7) return 'text-emerald-300';
  if (score >= 5) return 'text-brand/90';
  if (score >= 3) return 'text-orange-300';
  return 'text-red-300';
}

function SectionHeader({ icon: Icon, title, subtitle }) {
  return (
    <div className="flex items-start gap-3">
      <span className="mt-0.5 inline-flex h-7 w-7 items-center justify-center rounded-lg border border-white/10 bg-black/20">
        <Icon size={16} />
      </span>
      <div className="min-w-0">
        <div className="truncate text-sm font-semibold text-slate-200/90">{title}</div>
        {subtitle ? (
          <div className="mt-0.5 text-xs text-slate-300/70">{subtitle}</div>
        ) : null}
      </div>
    </div>
  );
}

function DriverList({ title, drivers, accent }) {
  const items = Array.isArray(drivers) ? drivers : [];

  return (
    <div className="space-y-2">
      <div className="text-xs font-semibold text-slate-300/70">{title}</div>
      {items.length === 0 ? (
        <div className="rounded-xl border border-white/10 bg-black/20 p-3 text-xs text-slate-300/70">
          Tidak ada driver.
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((d, idx) => {
            const mapped = typeof d?.mapped_score === 'number' ? d.mapped_score : d?.mapped_score;
            const label = (d?.finbert_label || '').toString();
            const headline = d?.headline ?? '';

            return (
              <div key={idx} className="rounded-xl border border-white/10 bg-black/20 p-3">
                <div className="flex items-start justify-between gap-3">
                  <div className="min-w-0 flex-1">
                    <div className="line-clamp-2 text-sm font-medium text-slate-200/90">{headline}</div>
                    <div className="mt-1 flex flex-wrap items-center gap-2">
                      <span
                        className={`inline-flex items-center rounded-full border px-2 py-0.5 text-[11px] font-semibold ${accent} border-white/10 bg-black/20`}
                      >
                        {label || '—'}
                      </span>
                    </div>
                  </div>

                  <div className="shrink-0 text-right">
                    <div className="text-[11px] text-slate-300/70">mapped score</div>
                    <div className={`text-lg font-extrabold ${accent}`}>
                      {typeof mapped === 'number' ? `${mapped}/10` : mapped ?? '—'}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default function TransparencyExplainability({
  analysis,
  sentiment,
  newsData,
  topPositiveDrivers,
  topNegativeDrivers
}) {
  const qualitative = analysis?.qualitative_analysis || {};
  const finbertResults = qualitative?.finbert_results || [];

  const headlinesFromBackend = newsData?.data?.headlines || [];
  const relevantCount = newsData?.data?.relevant_count;
  const totalFound = newsData?.data?.total_found;

  const scrapingSuccess = newsData?.success;
  const headlineCount = Array.isArray(headlinesFromBackend) ? headlinesFromBackend.length : 0;

  // Confidence/quality status (heuristic)
  const expectedMax = 10;
  const analysedCount = Array.isArray(finbertResults) ? finbertResults.length : 0;

  let scrapeStatus = 'data lengkap';
  let scrapeHint = '';
  if (scrapingSuccess === false) {
    scrapeStatus = 'data parsial (news unavailable)';
    scrapeHint = newsData?.error ? `(${newsData.error})` : '';
  } else if (
    headlineCount < expectedMax ||
    (typeof relevantCount === 'number' && relevantCount < expectedMax)
  ) {
    scrapeStatus = 'data parsial';
    scrapeHint = `(${headlineCount} headline untuk analisis)`;
  }

  const finalScore = sentiment?.score;
  const breakdown = sentiment?.breakdown || {};

  const quantitativeScore = breakdown?.quantitative_score;
  const finbertScore = breakdown?.finbert_score;

  const quantitativeWeight = breakdown?.quantitative_weight || '40%';
  const qualitativeWeight = breakdown?.qualitative_weight || '60%';

  const interpretation = sentiment?.interpretation || '';

  return (
    <div className="rounded-2xl border border-white/10 bg-white/[0.03] p-5 space-y-5">
      <SectionHeader
        icon={Sparkles}
        title="Transparansi & Explainability"
        subtitle="Alasan skor & rekomendasi diturunkan dari harga (Yahoo Finance) + news (CNBC World Markets)."
      />

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        <div className="lg:col-span-1 space-y-3">
          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-semibold text-slate-300/70">Sumber data</div>
            <div className="mt-2 space-y-2 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-200/90">Harga</span>
                <span className="text-slate-300/70">Yahoo Finance</span>
              </div>
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-200/90">News</span>
                <span className="text-slate-300/70">CNBC World Markets</span>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="flex items-center gap-2">
              <AlertTriangle
                size={16}
                className={scrapingSuccess === false ? 'text-orange-300' : 'text-slate-300/70'}
              />
              <div className="text-xs font-semibold text-slate-300/70">Confidence / kualitas input</div>
            </div>

            <div className="mt-3 space-y-2 text-sm">
              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-200/90">Headline dianalisis</span>
                <span className="text-slate-300/70">{analysedCount}</span>
              </div>

              <div className="flex items-center justify-between gap-3">
                <span className="text-slate-200/90">Status scraping</span>
                <span className="text-slate-300/70">{scrapeStatus}</span>
              </div>

              {scrapeHint ? <div className="text-xs text-slate-300/70">{scrapeHint}</div> : null}

              {typeof totalFound === 'number' ? (
                <div className="flex items-center justify-between gap-3">
                  <span className="text-slate-200/90">Total ditemukan</span>
                  <span className="text-slate-300/70">{totalFound}</span>
                </div>
              ) : null}

              {typeof relevantCount === 'number' ? (
                <div className="flex items-center justify-between gap-3">
                  <span className="text-slate-200/90">Relevan (filter)</span>
                  <span className="text-slate-300/70">{relevantCount}</span>
                </div>
              ) : null}

              {headlineCount === 0 && scrapingSuccess !== false ? (
                <div className="text-xs text-slate-300/70">Headline belum tersedia.</div>
              ) : null}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-4">
          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-semibold text-slate-300/70">Breakdown skor 1–10</div>
            <div className="mt-2 flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <div>
                <div className="text-xs text-slate-300/70">Final sentiment</div>
                <div className="mt-1 text-2xl font-extrabold">
                  <span className={scoreColor(finalScore)}>
                    {typeof finalScore === 'number' ? `${finalScore}/10` : '—'}
                  </span>
                </div>
              </div>
              <div className="sm:text-right">
                <div className="text-xs text-slate-300/70">Interpretasi</div>
                <div className="mt-1 text-sm font-medium text-slate-200/90">
                  {interpretation || '—'}
                </div>
              </div>
            </div>

            <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <div className="text-xs font-semibold text-slate-300/70">Kuantitatif</div>
                <div className="mt-1 flex items-baseline justify-between gap-3">
                  <div className="text-sm text-slate-200/90">Skor harga</div>
                  <div className="text-lg font-extrabold text-brand/90">
                    {typeof quantitativeScore === 'number' ? `${quantitativeScore}/10` : '—'}
                  </div>
                </div>
                <div className="mt-1 text-xs text-slate-300/70">Bobot: {quantitativeWeight}</div>
              </div>

              <div className="rounded-xl border border-white/10 bg-black/20 p-3">
                <div className="text-xs font-semibold text-slate-300/70">Kualitatif</div>
                <div className="mt-1 flex items-baseline justify-between gap-3">
                  <div className="text-sm text-slate-200/90">Skor FinBERT</div>
                  <div className="text-lg font-extrabold text-emerald-300">
                    {typeof finbertScore === 'number' ? `${Math.round(finbertScore)}/10` : '—'}
                  </div>
                </div>
                <div className="mt-1 text-xs text-slate-300/70">Bobot: {qualitativeWeight}</div>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-white/10 bg-black/20 p-4">
            <div className="text-xs font-semibold text-slate-300/70">Top drivers (dari headline)</div>
            <div className="mt-3 grid grid-cols-1 gap-4 sm:grid-cols-2">
              <DriverList
                title="Driver Positif"
                drivers={topPositiveDrivers}
                accent="text-emerald-300"
              />
              <DriverList
                title="Driver Negatif"
                drivers={topNegativeDrivers}
                accent="text-red-300"
              />
            </div>

            <div className="mt-3 text-xs text-slate-300/70">
              Catatan: Top drivers memakai skor FinBERT yang dipetakan ke skala 1–10.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}


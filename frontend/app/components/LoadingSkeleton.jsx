export default function LoadingSkeleton() {
  return (
    <div className="space-y-4">
      <div className="h-10 w-56 rounded-xl bg-white/5 bg-gradient-to-r from-white/5 via-white/10 to-white/5 bg-[length:200%_100%] animate-shimmer" />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        {[0, 1, 2].map((i) => (
          <div
            key={i}
            className="rounded-xl border border-white/10 bg-panel-1/10 p-4"
          >
            <div className="h-4 w-28 rounded bg-white/5" />
            <div className="mt-3 h-8 w-32 rounded bg-white/5" />
            <div className="mt-3 h-4 w-20 rounded bg-white/5" />
          </div>
        ))}
      </div>

      <div className="rounded-xl border border-white/10 bg-panel-1/10 p-4">
        <div className="h-4 w-40 rounded bg-white/5" />
        <div className="mt-4 h-[260px] w-full rounded bg-white/5" />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {[0, 1].map((i) => (
          <div
            key={i}
            className="rounded-xl border border-white/10 bg-panel-1/10 p-4"
          >
            <div className="h-4 w-44 rounded bg-white/5" />
            <div className="mt-4 space-y-3">
              {[0, 1, 2].map((j) => (
                <div key={j} className="h-10 w-full rounded bg-white/5" />
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}


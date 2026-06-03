import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

export default function PriceChart({ dates, closingPrices }) {
  const safeDates = Array.isArray(dates) && dates.length ? dates : [];
  const safePrices = Array.isArray(closingPrices) ? closingPrices : [];

  const data = safePrices.map((p, i) => {
    const date = safeDates[i] ?? `Day ${i + 1}`;
    return { date, price: p };
  });

  return (
    <div className="rounded-xl border border-white/10 bg-white/[0.03] p-4">
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm text-slate-200/75">Closing Prices</div>
          <div className="mt-1 text-lg font-semibold">7 Days Trend</div>
        </div>
      </div>

      <div className="mt-4 h-[260px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="rgba(148,163,184,0.15)" />
            <XAxis dataKey="date" hide />
            <YAxis
              tick={{ fill: 'rgba(226,232,240,0.8)' }}
              axisLine={{ stroke: 'rgba(148,163,184,0.2)' }}
              tickLine={false}
              width={40}
              domain={['auto', 'auto']}
            />
            <Tooltip
              contentStyle={{ background: 'rgba(2,6,23,0.95)', border: '1px solid rgba(255,255,255,0.08)' }}
              labelStyle={{ color: 'rgba(226,232,240,0.9)' }}
              itemStyle={{ color: 'rgba(226,232,240,0.9)' }}
              formatter={(value) => [Number(value).toFixed(2), 'Price']}
            />
            <Line
              type="monotone"
              dataKey="price"
              stroke="#60a5fa"
              strokeWidth={2.25}
              dot={false}
              activeDot={{ r: 4, fill: '#93c5fd', stroke: '#60a5fa', strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}


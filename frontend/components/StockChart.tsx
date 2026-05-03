import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts'
import { StockData } from '../types/api'

interface StockChartProps {
  data: StockData
}

export default function StockChart({ data }: StockChartProps) {
  const chartData = data.dates.map((date, index) => ({
    date: date.split('-').slice(1).join('/'), // Format MM/DD
    price: data.closing_prices[index],
  }))

  const avgPrice = data.average_price

  return (
    <ResponsiveContainer width="100%" height={250}>
      <LineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" strokeOpacity={0.3} />
        <XAxis 
          dataKey="date" 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
          minTickGap={8}
        />
        <YAxis 
          axisLine={false}
          tickLine={false}
          tick={{ fontSize: 12 }}
          tickFormatter={(value) => `$${value}`}
        />
        <Tooltip 
          formatter={(value: number) => [`$${value.toFixed(2)}`, 'Price']}
          labelFormatter={(label) => `Date: ${label}`}
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.1)'
          }}
        />
        <ReferenceLine 
          y={avgPrice} 
          label={{ value: `Avg: $${avgPrice.toFixed(2)}`, position: 'insideLeft' }}
          stroke="#f59e0b" 
          strokeDasharray="5 5"
          strokeWidth={2}
        />
        <Line 
          type="monotone" 
          dataKey="price" 
          stroke="#3b82f6" 
          strokeWidth={4}
          dot={{ fill: '#3b82f6', strokeWidth: 2 }}
          activeDot={{ r: 8, strokeWidth: 3 }}
        />
      </LineChart>
    </ResponsiveContainer>
  )
}


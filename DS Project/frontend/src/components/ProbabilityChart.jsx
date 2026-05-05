import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';

const ProbabilityChart = ({ transactions }) => {
  // Format data for chart - reverse to show oldest first
  const chartData = [...transactions]
    .reverse()
    .map((tx, index) => ({
      time: new Date(tx.timestamp).toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
      }),
      probability: parseFloat((tx.fraud_probability * 100).toFixed(2)),
      isFraud: tx.is_fraud_flag === 1,
    }));

  return (
    <div className="bg-fin-card border border-gray-800 rounded-xl p-6">
      <h2 className="text-lg font-semibold text-white mb-4">Suspicion Probability Trend</h2>
      
      <div className="h-48">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
            <XAxis
              dataKey="time"
              stroke="#6b7280"
              fontSize={10}
              tickLine={false}
            />
            <YAxis
              stroke="#6b7280"
              fontSize={10}
              tickLine={false}
              domain={[0, 100]}
              tickFormatter={(value) => `${value}%`}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#151520',
                border: '1px solid #2d3748',
                borderRadius: '8px',
                color: '#fff',
              }}
              formatter={(value) => [`${value}%`, 'Suspicion Probability']}
            />
            <Line
              type="monotone"
              dataKey="probability"
              stroke="#00d4ff"
              strokeWidth={2}
              dot={(props) => {
                const { cx, cy, payload } = props;
                return (
                  <circle
                    cx={cx}
                    cy={cy}
                    r={payload.isFraud ? 5 : 3}
                    fill={payload.isFraud ? '#ff4757' : '#00d4ff'}
                    stroke={payload.isFraud ? '#ff4757' : '#00d4ff'}
                  />
                );
              }}
              activeDot={{ r: 6, fill: '#00d4ff' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

        <div className="flex items-center justify-center gap-6 mt-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-fin-accent"></div>
          <span className="text-gray-400">Verified Safe</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-fraud-red"></div>
          <span className="text-gray-400">Marked Suspicious</span>
        </div>
      </div>
    </div>
  );
};

export default ProbabilityChart;

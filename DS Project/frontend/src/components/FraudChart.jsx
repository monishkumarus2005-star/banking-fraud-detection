import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const FraudChart = ({ legit, fraud }) => {
  const data = [
    { name: 'Verified Safe', value: legit, color: '#2ed573' },
    { name: 'Marked Suspicious', value: fraud, color: '#ff4757' },
  ];

  const COLORS = ['#2ed573', '#ff4757'];

  const renderCustomLabel = ({ name, value, percent }) => {
    if (value === 0) return null;
    return `${(percent * 100).toFixed(0)}%`;
  };

  return (
    <div className="bg-fin-card border border-gray-800 rounded-xl p-6">
      <h2 className="text-lg font-semibold text-white mb-4">Transaction Distribution</h2>
      
      <div className="h-64">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={renderCustomLabel}
              outerRadius={80}
              fill="#8884d8"
              dataKey="value"
            >
              {data.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#151520',
                border: '1px solid #2d3748',
                borderRadius: '8px',
                color: '#fff',
              }}
              formatter={(value) => [value.toLocaleString(), 'Count']}
            />
            <Legend
              verticalAlign="bottom"
              height={36}
              iconType="circle"
              formatter={(value, entry) => (
                <span style={{ color: entry.color }}>{value}</span>
              )}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-2 gap-4 mt-4">
        <div className="text-center">
          <p className="text-2xl font-bold text-legit-green">{legit.toLocaleString()}</p>
          <p className="text-gray-400 text-sm">Verified Safe</p>
        </div>
        <div className="text-center">
          <p className="text-2xl font-bold text-fraud-red">{fraud.toLocaleString()}</p>
          <p className="text-gray-400 text-sm">Marked Suspicious</p>
        </div>
      </div>
    </div>
  );
};

export default FraudChart;

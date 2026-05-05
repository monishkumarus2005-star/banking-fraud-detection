import React from 'react';
import { Clock, IndianRupee, AlertCircle } from 'lucide-react';

const LiveFeed = ({ transactions }) => {
  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 0,
    }).format(amount);
  };

  return (
    <div className="bg-fin-card border border-gray-800 rounded-xl overflow-hidden">
      <div className="p-6 border-b border-gray-800">
        <div className="flex items-center gap-2">
          <Clock className="w-5 h-5 text-fin-accent" />
          <h2 className="text-xl font-semibold text-white">Live Transaction Feed</h2>
        </div>
        <p className="text-gray-400 text-sm mt-1">
          Real-time incoming transactions with fraud probability
        </p>
      </div>

      <div className="max-h-[500px] overflow-y-auto">
        <table className="w-full">
          <thead className="bg-gray-900/50 sticky top-0">
            <tr>
              <th className="text-left py-3 px-4 text-gray-400 text-sm font-medium">Time</th>
              <th className="text-left py-3 px-4 text-gray-400 text-sm font-medium">Amount</th>
              <th className="text-left py-3 px-4 text-gray-400 text-sm font-medium">Suspicion Probability</th>
              <th className="text-left py-3 px-4 text-gray-400 text-sm font-medium">Status</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx) => (
              <tr
                key={tx.id}
                className={`border-t border-gray-800 transition-colors ${
                  tx.is_fraud_flag === 1
                    ? 'bg-red-500/10 hover:bg-red-500/20'
                    : 'hover:bg-gray-800/50'
                }`}
              >
                <td className="py-3 px-4 text-gray-300 text-sm">
                  {formatTime(tx.timestamp)}
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-1 text-white font-medium">
                    <IndianRupee className="w-4 h-4 text-gray-400" />
                    {formatAmount(tx.amount).replace('₹', '')}
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-24 bg-gray-700 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full transition-all ${
                          tx.fraud_probability > 0.5
                            ? 'bg-fraud-red'
                            : tx.fraud_probability > 0.3
                            ? 'bg-yellow-500'
                            : 'bg-legit-green'
                        }`}
                        style={{ width: `${tx.fraud_probability * 100}%` }}
                      />
                    </div>
                    <span className="text-sm text-gray-300">
                      {(tx.fraud_probability * 100).toFixed(1)}%
                    </span>
                  </div>
                </td>
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    {tx.is_fraud_flag === 1 ? (
                      <>
                        <AlertCircle className="w-4 h-4 text-fraud-red" />
                        <span className="text-fraud-red font-medium text-sm">Marked Suspicious</span>
                      </>
                    ) : (
                      <span className="text-legit-green font-medium text-sm">Verified Safe</span>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {transactions.length === 0 && (
          <div className="py-12 text-center text-gray-500">
            <p>Waiting for transactions...</p>
            <p className="text-sm mt-1">Transactions will appear here in real-time</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default LiveFeed;

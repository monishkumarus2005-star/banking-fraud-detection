import React from 'react';

const StatCard = ({ title, value, icon: Icon, color }) => {
  const colorClasses = {
    blue: 'from-blue-500/20 to-blue-600/10 border-blue-500/30',
    red: 'from-red-500/20 to-red-600/10 border-red-500/30',
    yellow: 'from-yellow-500/20 to-yellow-600/10 border-yellow-500/30',
    green: 'from-green-500/20 to-green-600/10 border-green-500/30',
  };

  const iconColors = {
    blue: 'text-blue-400',
    red: 'text-red-400',
    yellow: 'text-yellow-400',
    green: 'text-green-400',
  };

  return (
    <div className={`bg-gradient-to-br ${colorClasses[color]} border rounded-xl p-6 backdrop-blur-sm`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-gray-400 text-sm mb-1">{title}</p>
          <p className="text-3xl font-bold text-white">{value}</p>
        </div>
        <Icon className={`w-10 h-10 ${iconColors[color]}`} />
      </div>
    </div>
  );
};

export default StatCard;

import React, { useState, useEffect } from 'react';
import { Shield, AlertTriangle, Activity, TrendingUp } from 'lucide-react';
import LiveFeed from './components/LiveFeed';
import FraudChart from './components/FraudChart';
import ProbabilityChart from './components/ProbabilityChart';
import StatCard from './components/StatCard';
import './index.css';

const API_URL = 'http://localhost:9000';

function App() {
  const [transactions, setTransactions] = useState([]);
  const [stats, setStats] = useState({
    total_analyzed: 0,
    threats_blocked: 0,
    fraud_percentage: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  // Fetch data from API
  const fetchData = async () => {
    try {
      // Fetch recent transactions
      const txResponse = await fetch(`${API_URL}/transactions/recent`);
      const txData = await txResponse.json();
      setTransactions(txData);

      // Fetch stats
      const statsResponse = await fetch(`${API_URL}/stats`);
      const statsData = await statsResponse.json();
      setStats(statsData);
      setIsLoading(false);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  // Polling every 3 seconds
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-fin-dark flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-fin-accent mx-auto mb-4"></div>
          <p className="text-gray-400">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-fin-dark p-6">
      {/* Header */}
      <header className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Shield className="w-8 h-8 text-fin-accent" />
          <h1 className="text-3xl font-bold text-white">
            Transaction Fraud Detection <span className="text-gradient">System</span>
          </h1>
        </div>
        <p className="text-gray-400">
          Real-time transaction monitoring and suspicious activity detection powered by XGBoost
        </p>
      </header>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Analyzed"
          value={stats.total_analyzed.toLocaleString()}
          icon={Activity}
          color="blue"
        />
        <StatCard
          title="Suspicious Activity"
          value={stats.threats_blocked.toLocaleString()}
          icon={AlertTriangle}
          color="red"
        />
        <StatCard
          title="Suspicion Rate"
          value={`${stats.fraud_percentage}%`}
          icon={TrendingUp}
          color="yellow"
        />
        <StatCard
          title="Status"
          value="Active"
          icon={Shield}
          color="green"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Live Feed */}
        <div className="lg:col-span-2">
          <LiveFeed transactions={transactions} />
        </div>

        {/* Charts */}
        <div className="space-y-6">
          <FraudChart 
            legit={stats.total_analyzed - stats.threats_blocked} 
            fraud={stats.threats_blocked} 
          />
          <ProbabilityChart transactions={transactions} />
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-8 text-center text-gray-500 text-sm">
        <p>Powered by FastAPI + XGBoost + React | Amounts in INR (₹)</p>
      </footer>
    </div>
  );
}

export default App;

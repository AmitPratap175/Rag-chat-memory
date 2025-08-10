import React, { useState, useEffect } from 'react';

interface Stats {
  num_passages: number;
  num_questions: number;
}

const Dashboard: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        setStats(data);
      } catch (error) {
        console.error("Failed to fetch stats:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="page-container">
      <h1>Dashboard</h1>
      <div className="stats-container">
        <div className="stat-card">
          <h2>Total Passages</h2>
          <p>{stats?.num_passages}</p>
        </div>
        <div className="stat-card">
          <h2>Total Questions</h2>
          <p>{stats?.num_questions}</p>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

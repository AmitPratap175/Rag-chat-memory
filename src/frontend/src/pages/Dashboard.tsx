import React, { useState, useEffect } from 'react';
import { CardContent, Typography, CircularProgress, Box, Paper } from '@mui/material';
import { Description, HelpOutline } from '@mui/icons-material';

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
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom component="div" sx={{ color: 'var(--on-surface)' }}>
        Dashboard
      </Typography>
      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 3 }}>
        <Box sx={{ flex: '1 1 calc(50% - 12px)', minWidth: { xs: '100%', sm: 'calc(50% - 12px)', md: 'calc(33.33% - 12px)' } }}>
          <Paper elevation={3} sx={{ backgroundColor: 'var(--surface)', color: 'var(--on-surface)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Description sx={{ mr: 1, color: 'var(--primary)' }} />
                <Typography variant="h6" component="div">
                  Total Passages
                </Typography>
              </Box>
              <Typography variant="h3" component="div">
                {stats?.num_passages}
              </Typography>
            </CardContent>
          </Paper>
        </Box>
        <Box sx={{ flex: '1 1 calc(50% - 12px)', minWidth: { xs: '100%', sm: 'calc(50% - 12px)', md: 'calc(33.33% - 12px)' } }}>
          <Paper elevation={3} sx={{ backgroundColor: 'var(--surface)', color: 'var(--on-surface)' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <HelpOutline sx={{ mr: 1, color: 'var(--primary)' }} />
                <Typography variant="h6" component="div">
                  Total Questions
                </Typography>
              </Box>
              <Typography variant="h3" component="div">
                {stats?.num_questions}
              </Typography>
            </CardContent>
          </Paper>
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
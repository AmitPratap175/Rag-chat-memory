import React, { useState, useEffect } from 'react';
import {
  Typography,
  Box,
  CircularProgress,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';

interface CrawlJob {
  id: string;
  url: string;
  status: 'Pending' | 'In Progress' | 'Completed' | 'Failed';
  startedAt: string;
  completedAt?: string;
}

const CrawlManagement: React.FC = () => {
  const [crawlJobs, setCrawlJobs] = useState<CrawlJob[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Simulate fetching data
    const fetchCrawlJobs = () => {
      setLoading(true);
      setTimeout(() => {
        const dummyData: CrawlJob[] = [
          {
            id: 'job-1',
            url: 'https://example.com/docs/1',
            status: 'Completed',
            startedAt: '2023-01-01T10:00:00Z',
            completedAt: '2023-01-01T10:15:00Z',
          },
          {
            id: 'job-2',
            url: 'https://example.com/docs/2',
            status: 'In Progress',
            startedAt: '2023-01-02T11:00:00Z',
          },
          {
            id: 'job-3',
            url: 'https://example.com/docs/3',
            status: 'Pending',
            startedAt: '2023-01-03T12:00:00Z',
          },
        ];
        setCrawlJobs(dummyData);
        setLoading(false);
      }, 1500);
    };

    fetchCrawlJobs();
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
        Crawl Management
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, color: 'var(--on-surface)' }}>
        Monitor the status of your web crawling jobs.
      </Typography>

      {crawlJobs.length === 0 ? (
        <Typography variant="h6" sx={{ color: 'var(--on-surface)' }}>
          No crawl jobs found.
        </Typography>
      ) : (
        <TableContainer component={Paper} sx={{ backgroundColor: 'var(--surface)' }}>
          <Table sx={{ minWidth: 650 }} aria-label="crawl jobs table">
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Job ID</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>URL</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Status</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Started At</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Completed At</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {crawlJobs.map((job) => (
                <TableRow
                  key={job.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row" sx={{ color: 'var(--on-surface)' }}>
                    {job.id}
                  </TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{job.url}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{job.status}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{new Date(job.startedAt).toLocaleString()}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>
                    {job.completedAt ? new Date(job.completedAt).toLocaleString() : 'N/A'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default CrawlManagement;
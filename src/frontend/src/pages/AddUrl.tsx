import React, { useState } from 'react';
import { TextField, Button, Typography, Box, Snackbar, Alert, Radio, RadioGroup, FormControlLabel, FormControl, FormLabel } from '@mui/material';

const AddUrl: React.FC = () => {
  const [urls, setUrls] = useState('');
  const [crawlMode, setCrawlMode] = useState<'single' | 'recursive'>('recursive'); // New state for crawl mode
  const [message, setMessage] = useState<{ text: string; type: 'success' | 'error' | 'info' | 'warning' | undefined } | null>(null);
  const [openSnackbar, setOpenSnackbar] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const urlList = urls.split('\n').filter(url => url.trim() !== '');

    if (urlList.length === 0) {
      setMessage({ text: 'Please enter at least one URL.', type: 'warning' });
      setOpenSnackbar(true);
      return;
    }

    try {
      const response = await fetch('/api/crawl', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ urls: urlList, crawl_mode: crawlMode }), // Include crawl_mode
      });

      const data = await response.json();
      if (response.ok) {
        setMessage({ text: data.message || 'URLs submitted successfully!', type: 'success' });
        setUrls(''); // Clear input on success
      } else {
        setMessage({ text: data.error || 'Failed to submit URLs.', type: 'error' });
      }
    } catch (error) {
      console.error("Failed to fetch:", error);
      setMessage({ text: 'Network error or server is unreachable.', type: 'error' });
    } finally {
      setOpenSnackbar(true);
    }
  };

  const handleCloseSnackbar = (event?: React.SyntheticEvent | Event, reason?: string) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpenSnackbar(false);
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom component="div" sx={{ color: 'var(--on-surface)' }}>
        Add URLs to Crawl
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, color: 'var(--on-surface)' }}>
        Enter one or more URLs below, each on a new line, to add them to the crawling queue.
      </Typography>
      <form onSubmit={handleSubmit}>
        <FormControl component="fieldset" sx={{ mb: 2 }}>
          <FormLabel component="legend" sx={{ color: 'var(--on-surface)' }}>Crawl Mode</FormLabel>
          <RadioGroup
            row
            name="crawl-mode-group"
            value={crawlMode}
            onChange={(event) => setCrawlMode(event.target.value as 'single' | 'recursive')}
          >
            <FormControlLabel value="single" control={<Radio sx={{ color: 'var(--primary)' }} />} label="Single Page" sx={{ color: 'var(--on-surface)' }} />
            <FormControlLabel value="recursive" control={<Radio sx={{ color: 'var(--primary)' }} />} label="Recursive" sx={{ color: 'var(--on-surface)' }} />
          </RadioGroup>
        </FormControl>
        <TextField
          label="URLs"
          multiline
          rows={10}
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          placeholder="e.g.\nhttps://example.com/page1\nhttps://example.com/page2"
          variant="outlined"
          fullWidth
          sx={{
            mb: 2,
            backgroundColor: 'var(--surface)',
            '.MuiInputBase-input': { color: 'var(--on-surface)' },
            '.MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
            '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--primary)' },
            '.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--primary)' },
            '.MuiInputLabel-root': { color: '#e0e0e0' },
            '.Mui-focused': { color: 'var(--primary)' },
          }}
        />
        <Button
          type="submit"
          variant="contained"
          sx={{
            backgroundColor: 'var(--primary)',
            color: 'var(--on-primary)',
            '&:hover': { backgroundColor: '#a050d0' },
          }}
        >
          Crawl URLs
        </Button>
      </form>
      <Snackbar open={openSnackbar} autoHideDuration={6000} onClose={handleCloseSnackbar}>
        <Alert onClose={handleCloseSnackbar} severity={message?.type} sx={{ width: '100%' }}>
          {message?.text}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default AddUrl;

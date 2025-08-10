import React, { useState } from 'react';

const AddUrl: React.FC = () => {
  const [urls, setUrls] = useState('');
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    const urlList = urls.split('\n').filter(url => url.trim() !== '');

    const response = await fetch('/api/crawl', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ urls: urlList }),
    });

    const data = await response.json();
    setMessage(data.message || data.error);
  };

  return (
    <div className="page-container">
      <h1>Add URLs to Crawl</h1>
      <form onSubmit={handleSubmit}>
        <textarea
          value={urls}
          onChange={(e) => setUrls(e.target.value)}
          placeholder="Enter one URL per line"
          className="url-textarea"
        />
        <button type="submit" className="submit-button">
          Crawl URLs
        </button>
      </form>
      {message && <p className="message">{message}</p>}
    </div>
  );
};

export default AddUrl;

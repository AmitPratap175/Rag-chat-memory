import React, { useState, useEffect, ChangeEvent, KeyboardEvent, useRef } from 'react';
import { useWebSocket } from '../services/useWebSocket';
import EE from '../components/easter_egg/ee';
import { Box, TextField, Typography, Paper, List, ListItem, ListItemText, IconButton, InputAdornment, CircularProgress } from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import MenuIcon from '@mui/icons-material/Menu';


const Chat: React.FC = () => {
  const [messages, setMessages] = useState<{ user: string; msg: string }[]>([
    { user: 'Bot', msg: 'Welcome! How can I help you today?' }
  ]);
  const [input, setInput] = useState('');
  const [showEE, setShowEE] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
  const { response, isOpen, isCrawling, sendMessage } = useWebSocket(`${wsProtocol}${window.location.host}/ws`, setShowEE);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (response) {
      setMessages((prev) => [...prev, { user: 'Bot', msg: response }]);
    }
  }, [response]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => setInput(e.target.value);

  const handleSubmit = () => {
    if (input.trim()) {
      setMessages([...messages, { user: 'User', msg: input }]);
      setInput('');
      if (isOpen) sendMessage(input);
    }
  };

  useEffect(() => {
    if (isCrawling) {
      setMessages(prev => [...prev, { user: 'Bot', msg: 'Crawling URL and generating questions...' }]);
    }
  }, [isCrawling]);

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => {
      const base64 = reader.result as string;
      sendMessage(base64);
      setMessages(prev => [...prev, { user: 'Bot', msg: `Uploading ${file.name}...` }]);
    };
    event.target.value = ""; // Reset file input
  };

  // Message formatting helper
  const renderBotMsg = (text: string): JSX.Element => {
    const formatText = (str: string) => {
      const parts = str.split(/(\*.\*.*?\*\*)/g);
      return parts.map((part, index) => {
        if (part.startsWith('**') && part.endsWith('**')) {
          return <strong key={index}>{part.slice(2, -2)}</strong>;
        }
        return part;
      });
    };

    const lines = text.split('\n').filter(l => l.trim() !== '');
    const bulletPattern = /^\s*([*•-])\s+/; // Fixed: removed unnecessary escape character
    const bulletLines = lines.filter(line => bulletPattern.test(line));

    if (bulletLines.length > 0 && bulletLines.length >= Math.max(2, lines.length - 1)) {
      return (
        <List sx={{ textAlign: "left", paddingLeft: "1.4em" }}>
          {lines.map((line, idx) =>
            bulletPattern.test(line) ? (
              <ListItem key={idx} disablePadding>
                <ListItemText primary={formatText(line.replace(bulletPattern, ''))} />
              </ListItem>
            ) : null
          )}
        </List>
      );
    }

    return (
      <Typography component="span" sx={{ display: "block", textAlign: "left", whiteSpace: "pre-wrap" }}>
        {formatText(text)}
      </Typography>
    );
  };

  

  return (
    <Box sx={{ display: 'flex', height: '100vh', backgroundColor: 'var(--background)' }}>
      {/* Main Chat UI */}
      <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', backgroundColor: 'var(--background)' }}>
        <Paper elevation={2} sx={{ p: 2, backgroundColor: 'var(--surface)', display: 'flex', alignItems: 'center', borderBottom: '1px solid #333' }}>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            sx={{ mr: 2, display: { md: 'none' }, color: 'var(--on-surface)' }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" sx={{ flexGrow: 1, color: 'var(--on-surface)' }}>
            FicAssist Chat
          </Typography>
        </Paper>

        <Box sx={{ flexGrow: 1, overflowY: 'auto', p: 3 }}>
          {messages.map((msg, idx) => (
            <Box
              key={idx}
              sx={{
                display: 'flex',
                justifyContent: msg.user === 'User' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  borderRadius: msg.user === 'User' ? '20px 20px 4px 20px' : '20px 20px 20px 4px',
                  backgroundColor: msg.user === 'User' ? 'var(--primary)' : 'var(--surface)',
                  color: msg.user === 'User' ? 'var(--on-primary)' : 'var(--on-surface)',
                  maxWidth: '70%',
                  wordBreak: 'break-word',
                  borderColor: msg.user === 'User' ? 'transparent' : '#333',
                }}
              >
                {msg.user === 'Bot' ? renderBotMsg(msg.msg) : msg.msg}
              </Paper>
            </Box>
          ))}
          {isCrawling && (
            <Box sx={{ display: 'flex', justifyContent: 'flex-start', mb: 2 }}>
              <Paper
                variant="outlined"
                sx={{
                  p: 1.5,
                  borderRadius: '20px 20px 20px 4px',
                  backgroundColor: 'var(--surface)',
                  color: 'var(--on-surface)',
                  maxWidth: '70%',
                  wordBreak: 'break-word',
                  borderColor: '#333',
                }}
              >
                <CircularProgress size={20} sx={{ mr: 1 }} />
                <Typography component="span">Crawling URL and generating questions...</Typography>
              </Paper>
            </Box>
          )}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ p: 2, borderTop: '1px solid #333', display: 'flex', alignItems: 'center', gap: 2 }}>
          <input
            id="pdf-upload"
            type="file"
            accept="application/pdf"
            style={{ display: 'none' }}
            onChange={handleFileChange}
          />
          <label htmlFor="pdf-upload">
            <IconButton component="span" sx={{ color: 'var(--primary)' }}>
              <AttachFileIcon />
            </IconButton>
          </label>
          <TextField
            fullWidth
            variant="outlined"
            placeholder="Type your message..."
            value={input}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            sx={{
              backgroundColor: 'var(--surface)',
              '.MuiInputBase-input': { color: 'var(--on-surface)' },
              '.MuiOutlinedInput-notchedOutline': { borderColor: '#333' },
              '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--primary)' },
              '.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: 'var(--primary)' },
              borderRadius: '20px',
              '& .MuiOutlinedInput-root': {
                borderRadius: '20px',
                paddingRight: '0px', // Adjust padding to make room for adornment
              },
            }}
            InputProps={{
              endAdornment: (
                <InputAdornment position="end">
                  <IconButton
                    onClick={handleSubmit}
                    disabled={!input.trim()}
                    sx={{
                      backgroundColor: 'var(--primary)',
                      color: 'var(--on-primary)',
                      '&:hover': { backgroundColor: '#a050d0' },
                      borderRadius: '50%',
                      p: 1,
                    }}
                  >
                    <SendIcon />
                  </IconButton>
                </InputAdornment>
              ),
            }}
          />
        </Box>
        {showEE && <EE />}
      </Box>
    </Box>
  );
};

export default Chat;
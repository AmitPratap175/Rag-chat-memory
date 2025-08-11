import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';
import {
  Typography,
  Box,
  Button,
  CircularProgress,
  Paper,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
} from '@mui/material';
import CheckCircleOutlineIcon from '@mui/icons-material/CheckCircleOutline';
import CancelOutlinedIcon from '@mui/icons-material/CancelOutlined';

const QuizPlayer: React.FC = () => {
  const [quizState, setQuizState] = useState('idle'); // idle, playing, finished
  const [question, setQuestion] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const ws = useRef<WebSocket | null>(null);
  const userUuid = useRef<string>(uuidv4());

  useEffect(() => {
    const wsProtocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
    const wsUrl = `${wsProtocol}${window.location.host}/ws/quiz`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      console.log("Quiz WebSocket connected");
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.event === 'question') {
        setQuestion(data.payload);
        setResult(null);
        setLoading(false);
      } else if (data.event === 'answer_result') {
        setResult(data.payload);
      } else if (data.event === 'quiz_finished') {
        setQuizState('finished');
        setLoading(false);
      }
    };

    ws.current.onclose = () => {
      console.log("Quiz WebSocket disconnected");
    };

    return () => {
      ws.current?.close();
    };
  }, []);

  const startQuiz = () => {
    setLoading(true);
    ws.current?.send(JSON.stringify({ event: 'start_quiz', payload: { uuid: userUuid.current } }));
    setQuizState('playing');
  };

  const submitAnswer = (answer: string) => {
    setLoading(true);
    ws.current?.send(JSON.stringify({ event: 'answer', payload: { question_id: question.id, answer: answer } }));
  };

  const nextQuestion = () => {
    setLoading(true);
    ws.current?.send(JSON.stringify({ event: 'next_question' }));
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <CircularProgress />
      </Box>
    );
  }

  if (quizState === 'idle') {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ color: 'var(--on-surface)' }}>
          VARC Quiz
        </Typography>
        <Button
          variant="contained"
          sx={{
            backgroundColor: 'var(--primary)',
            color: 'var(--on-primary)',
            '&:hover': { backgroundColor: '#a050d0' },
          }}
          onClick={startQuiz}
        >
          Start Quiz
        </Button>
      </Box>
    );
  }

  if (quizState === 'finished') {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <Typography variant="h4" gutterBottom sx={{ color: 'var(--on-surface)' }}>
          Quiz Finished!
        </Typography>
        <Button
          variant="contained"
          sx={{
            backgroundColor: 'var(--primary)',
            color: 'var(--on-primary)',
            '&:hover': { backgroundColor: '#a050d0' },
          }}
          onClick={startQuiz}
        >
          Play Again
        </Button>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ color: 'var(--on-surface)' }}>
        VARC Quiz
      </Typography>
      {question && (
        <Paper elevation={3} sx={{ p: 3, mb: 3, backgroundColor: 'var(--surface)', color: 'var(--on-surface)' }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            {question.question_text}
          </Typography>
          <List>
            {question.options.map((option: string, index: number) => (
              <ListItem key={index} disablePadding>
                <ListItemButton
                  onClick={() => submitAnswer(option.charAt(0))}
                  disabled={!!result}
                  sx={{
                    mb: 1,
                    backgroundColor: result && option.charAt(0) === result.correct_answer ? '#4CAF5033' : 'transparent',
                    '&:hover': { backgroundColor: result ? 'transparent' : '#2c2c2c' },
                  }}
                >
                  <ListItemText primary={option} sx={{ color: 'var(--on-surface)' }} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
      {result && (
        <Paper elevation={3} sx={{ p: 3, mt: 3, backgroundColor: 'var(--surface)', color: 'var(--on-surface)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            {result.is_correct ? (
              <CheckCircleOutlineIcon sx={{ color: '#4CAF50', mr: 1 }} />
            ) : (
              <CancelOutlinedIcon sx={{ color: '#F44336', mr: 1 }} />
            )}
            <Typography variant="h6" sx={{ color: result.is_correct ? '#4CAF50' : '#F44336' }}>
              {result.is_correct ? 'Correct!' : 'Incorrect!'}
            </Typography>
          </Box>
          <Typography variant="body1" sx={{ mb: 2 }}>{result.explanation}</Typography>
          <Button
            variant="contained"
            sx={{
              backgroundColor: 'var(--primary)',
              color: 'var(--on-primary)',
              '&:hover': { backgroundColor: '#a050d0' },
            }}
            onClick={nextQuestion}
          >
            Next Question
          </Button>
        </Paper>
      )}
    </Box>
  );
};

export default QuizPlayer;
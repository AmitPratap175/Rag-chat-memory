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
  Button,
} from '@mui/material';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

interface Question {
  id: number;
  type: string;
  difficulty: number;
  json_payload: {
    question_text: string;
  };
}

const QuestionBank: React.FC = () => {
  const [questions, setQuestions] = useState<Question[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchQuestions = async () => {
    try {
      const response = await fetch('/api/questions');
      const data = await response.json();
      setQuestions(data);
    } catch (error) {
      console.error("Failed to fetch questions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchQuestions();
  }, []);

  const handleDelete = async (id: number) => {
    if (window.confirm('Are you sure you want to delete this question?')) {
      try {
        await fetch(`/api/questions/${id}`, { method: 'DELETE' });
        fetchQuestions(); // Re-fetch questions after deletion
      } catch (error) {
        console.error("Failed to delete question:", error);
      }
    }
  };

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
        Question Bank & Curation
      </Typography>
      <Typography variant="body1" sx={{ mb: 3, color: 'var(--on-surface)' }}>
        Manage and curate your generated questions.
      </Typography>

      {questions.length === 0 ? (
        <Typography variant="h6" sx={{ color: 'var(--on-surface)' }}>
          No questions found in the bank.
        </Typography>
      ) : (
        <TableContainer component={Paper} sx={{ backgroundColor: 'var(--surface)' }}>
          <Table sx={{ minWidth: 650 }} aria-label="question bank table">
            <TableHead>
              <TableRow>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>ID</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Type</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Question</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Difficulty</TableCell>
                <TableCell sx={{ color: 'var(--on-surface)', fontWeight: 'bold' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {questions.map((q) => (
                <TableRow
                  key={q.id}
                  sx={{ '&:last-child td, &:last-child th': { border: 0 } }}
                >
                  <TableCell component="th" scope="row" sx={{ color: 'var(--on-surface)' }}>
                    {q.id}
                  </TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{q.type}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{q.json_payload.question_text}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>{q.difficulty}</TableCell>
                  <TableCell sx={{ color: 'var(--on-surface)' }}>
                    <Button
                      variant="outlined"
                      startIcon={<EditIcon />}
                      sx={{
                        mr: 1,
                        borderColor: '#555',
                        color: 'var(--on-surface)',
                        '&:hover': { borderColor: 'var(--primary)', color: 'var(--primary)' },
                      }}
                      onClick={() => alert("Edit functionality not implemented yet.")}
                    >
                      Edit
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      sx={{
                        borderColor: '#555',
                        color: 'var(--on-surface)',
                        '&:hover': { borderColor: 'var(--error)', color: 'var(--error)' },
                      }}
                      onClick={() => handleDelete(q.id)}
                    >
                      Delete
                    </Button>
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

export default QuestionBank;
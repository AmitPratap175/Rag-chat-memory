import React, { useState, useEffect } from 'react';

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
    await fetch(`/api/questions/${id}`, { method: 'DELETE' });
    fetchQuestions();
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="page-container">
      <h1>Question Bank & Curation</h1>
      <table className="question-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Question</th>
            <th>Difficulty</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {questions.map((q) => (
            <tr key={q.id}>
              <td>{q.id}</td>
              <td>{q.type}</td>
              <td>{q.json_payload.question_text}</td>
              <td>{q.difficulty}</td>
              <td>
                <button className="action-button" onClick={() => alert("Edit functionality not implemented yet.")}>Edit</button>
                <button className="action-button" onClick={() => handleDelete(q.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default QuestionBank;

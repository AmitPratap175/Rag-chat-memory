import React, { useState, useEffect, useRef } from 'react';
import { v4 as uuidv4 } from 'uuid';

const QuizPlayer: React.FC = () => {
  const [quizState, setQuizState] = useState('idle'); // idle, playing, finished
  const [question, setQuestion] = useState<any>(null);
  const [result, setResult] = useState<any>(null);
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
      } else if (data.event === 'answer_result') {
        setResult(data.payload);
      } else if (data.event === 'quiz_finished') {
        setQuizState('finished');
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
    ws.current?.send(JSON.stringify({ event: 'start_quiz', payload: { uuid: userUuid.current } }));
    setQuizState('playing');
  };

  const submitAnswer = (answer: string) => {
    ws.current?.send(JSON.stringify({ event: 'answer', payload: { question_id: question.id, answer: answer } }));
  };

  const nextQuestion = () => {
    ws.current?.send(JSON.stringify({ event: 'next_question' }));
  }

  if (quizState === 'idle') {
    return (
      <div className="page-container">
        <h1>VARC Quiz</h1>
        <button onClick={startQuiz} className="submit-button">Start Quiz</button>
      </div>
    );
  }

  if (quizState === 'finished') {
    return (
      <div className="page-container">
        <h1>Quiz Finished!</h1>
        <button onClick={startQuiz} className="submit-button">Play Again</button>
      </div>
    );
  }

  return (
    <div className="page-container">
      <h1>VARC Quiz</h1>
      {question && (
        <div>
          <h3>{question.question_text}</h3>
          <div>
            {question.options.map((option: string, index: number) => (
              <button key={index} onClick={() => submitAnswer(option.charAt(0))} className="option-button">
                {option}
              </button>
            ))}
          </div>
        </div>
      )}
      {result && (
        <div className="result-container">
          <h4 className={result.is_correct ? 'correct' : 'incorrect'}>
            {result.is_correct ? 'Correct!' : 'Incorrect!'}
          </h4>
          <p>{result.explanation}</p>
          <button onClick={nextQuestion} className="submit-button">Next Question</button>
        </div>
      )}
    </div>
  );
};

export default QuizPlayer;

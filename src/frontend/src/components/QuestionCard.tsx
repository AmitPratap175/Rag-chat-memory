import React, { useState } from 'react';
import { Card, Button } from 'react-bootstrap';

interface Option {
    [key: string]: string;
}

interface Question {
    question_number: number;
    question_text: string;
    options: Option;
    solution: string;
    correct_answer: string;
    image_urls: string[];
    subject: string;
    instructions: string;
}

interface Props {
    question: Question;
}

const QuestionCard: React.FC<Props> = ({ question }) => {
    const [showSolution, setShowSolution] = useState(false);

    return (
        <Card className="mb-3 bg-dark text-white">
            <Card.Body>
                <Card.Title>Question {question.question_number}</Card.Title>
                {question.instructions && <p style={{ whiteSpace: 'pre-wrap' }}><strong>Instructions:</strong> {question.instructions}</p>}
                <p style={{ whiteSpace: 'pre-wrap' }}>{question.question_text}</p>
                {question.image_urls.map((url, index) => (
                    <img key={index} src={url} alt={`Question ${question.question_number}`} className="img-fluid mb-3" />
                ))}
                <div className="options">
                    {Object.entries(question.options).map(([key, value]) => (
                        <div key={key} className="mb-2">
                            <strong>{key}:</strong> {value}
                        </div>
                    ))}
                </div>
                <Button variant="primary" onClick={() => setShowSolution(!showSolution)}>
                    {showSolution ? 'Hide' : 'Show'} Solution
                </Button>
                {showSolution && (
                    <div className="mt-3">
                        <h5>Solution</h5>
                        <p style={{ whiteSpace: 'pre-wrap' }}>{question.solution}</p>
                        <p><strong>Correct Answer: {question.correct_answer}</strong></p>
                    </div>
                )}
            </Card.Body>
        </Card>
    );
};

export default QuestionCard;

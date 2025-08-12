import React, { useState, useEffect } from 'react';
import QuestionCard from '../components/QuestionCard';

interface Question {
    question_number: number;
    question_text: string;
    options: { [key: string]: string };
    solution: string;
    correct_answer: string;
    image_urls: string[];
    subject: string;
    instructions: string;
}

const QuantPage: React.FC = () => {
    const [questions, setQuestions] = useState<Question[]>([]);

    useEffect(() => {
        fetch('/quant_question_bank.json')
            .then(response => response.json())
            .then(data => setQuestions(data));
    }, []);

    return (
        <div className="container mt-4">
            <h1 className="text-white">Quant Questions</h1>
            {questions.map(q => (
                <QuestionCard key={q.question_number} question={q} />
            ))}
        </div>
    );
};

export default QuantPage;

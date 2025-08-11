import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css';
import Dashboard from './pages/Dashboard';
import AddUrl from './pages/AddUrl';
import CrawlManagement from './pages/CrawlManagement';
import QuestionBank from './pages/QuestionBank';
import QuizPlayer from './pages/QuizPlayer';
import Chat from './pages/Chat';
import Layout from './components/Layout';

const App: React.FC = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/add-url" element={<AddUrl />} />
          <Route path="/crawls" element={<CrawlManagement />} />
          <Route path="/questions" element={<QuestionBank />} />
          <Route path="/quiz" element={<QuizPlayer />} />
          <Route path="/chat" element={<Chat />} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;

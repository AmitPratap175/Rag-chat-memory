import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import NavigationBar from './components/NavigationBar';
import HomePage from './pages/HomePage';
import VarcPage from './pages/VarcPage';
import QuantPage from './pages/QuantPage';
import DilrPage from './pages/DilrPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <NavigationBar />
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/varc" element={<VarcPage />} />
          <Route path="/quant" element={<QuantPage />} />
          <Route path="/dilr" element={<DilrPage />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
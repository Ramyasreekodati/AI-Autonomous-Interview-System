import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Interview from './pages/Interview';
import Dashboard from './pages/Dashboard';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Routes>
          <Route path="/" element={<Login />} />
          <Route path="/interview/:id" element={<Interview />} />
          <Route path="/dashboard/:id" element={<Dashboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

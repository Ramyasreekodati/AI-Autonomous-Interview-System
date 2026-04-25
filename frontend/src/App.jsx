import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Login from './pages/Login';
import Interview from './pages/Interview';
import Dashboard from './pages/Dashboard';
import Result from './pages/Result';
import EliteDashboard from './pages/elite/EliteDashboard';
import EliteInterview from './pages/elite/EliteInterview';
import './index.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/interview/:id" element={<Interview />} />
          <Route path="/result/:id" element={<Result />} />
          <Route path="/login" element={<Login />} />
          
          {/* Elite Premium Routes */}
          <Route path="/elite/dashboard" element={<EliteDashboard />} />
          <Route path="/elite/interview/:id" element={<EliteInterview />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;

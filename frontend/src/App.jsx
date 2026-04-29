import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import PracticeRoom from './components/PracticeRoom';
import MyVideos from './components/MyVideos';
import Roulette from './components/Roulette';
import ResumeScanner from './components/ResumeScanner';
import Curriculum from './components/Curriculum';
import Certificate from './components/Certificate';
import RecruiterDashboard from './components/RecruiterDashboard';
import './index.css'; 

function App() {
  const [currentView, setCurrentView] = useState('landing');

  return (
    <div className="app-container">
      <Sidebar currentView={currentView} setCurrentView={setCurrentView} />
      
      <main className="main-content" id="main-view">
        {currentView === 'landing' && (
          <section id="view-landing" className="animate-fade">
            <div className="hero" style={{ padding: 'var(--spacing-xl) 0' }}>
              <h1 style={{ marginBottom: 'var(--spacing-md)' }}>Practice makes <br/><span style={{ color: 'var(--accent-teal)' }}>Placement.</span></h1>
              <p style={{ fontSize: '1.2rem', maxWidth: '600px', marginBottom: 'var(--spacing-lg)' }}>
                Don't just read advice. Practice with our state-of-the-art AI Interview Coach. Get real-time feedback on your pace, confidence, and content.
              </p>
              <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
                <button className="btn btn-primary" onClick={() => setCurrentView('practice')}>
                  Start Mock Interview <i className="fas fa-arrow-right"></i>
                </button>
                <button className="btn btn-outline" onClick={() => setCurrentView('dashboard')}>Go to Dashboard</button>
              </div>
            </div>
          </section>
        )}

        {currentView === 'dashboard' && <Dashboard setView={setCurrentView} />}
        {currentView === 'practice' && <PracticeRoom setView={setCurrentView} />}
        {currentView === 'roulette' && <Roulette setView={setCurrentView} />}
        {currentView === 'videos' && <MyVideos />}
        {currentView === 'lessons' && <Curriculum setView={setCurrentView} />}
        {currentView === 'resume' && <ResumeScanner />}
        {currentView === 'certificates' && <Certificate />}
        {currentView === 'recruiter' && <RecruiterDashboard />}
        
      </main>
    </div>
  );
}

export default App;

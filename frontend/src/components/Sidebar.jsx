import React from 'react';

const Sidebar = ({ currentView, setCurrentView }) => {
  return (
    <aside className="sidebar">
      <div className="logo">
        <i className="fas fa-brain"></i>
        <span>InterviewAI</span>
      </div>
      <nav className="nav-links">
        <ul>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'landing' ? 'active' : ''}`}
              onClick={() => setCurrentView('landing')}
            >
              <i className="fas fa-home"></i> Home
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'dashboard' ? 'active' : ''}`}
              onClick={() => setCurrentView('dashboard')}
            >
              <i className="fas fa-chart-line"></i> Dashboard
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'practice' ? 'active' : ''}`}
              onClick={() => setCurrentView('practice')}
            >
              <i className="fas fa-video"></i> Practice Room
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'videos' ? 'active' : ''}`}
              onClick={() => setCurrentView('videos')}
            >
              <i className="fas fa-video"></i> My Videos
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'lessons' ? 'active' : ''}`}
              onClick={() => setCurrentView('lessons')}
            >
              <i className="fas fa-book-open"></i> Curriculum
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'certificates' ? 'active' : ''}`}
              onClick={() => setCurrentView('certificates')}
            >
              <i className="fas fa-certificate"></i> Certifications
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'resume' ? 'active' : ''}`}
              onClick={() => setCurrentView('resume')}
            >
              <i className="fas fa-file-alt"></i> Resume AI
            </a>
          </li>
          <li className="nav-item">
            <a 
              href="#" 
              className={`nav-link ${currentView === 'recruiter' ? 'active' : ''}`}
              onClick={() => setCurrentView('recruiter')}
            >
              <i className="fas fa-user-shield"></i> Recruiter Mode
            </a>
          </li>
        </ul>
      </nav>
      <div className="sidebar-footer">
        <div className="glass" style={{ padding: '1rem', marginTop: 'auto' }}>
          <p style={{ fontSize: '0.8rem', marginBottom: '0.5rem' }}>Pro Plan Active</p>
          <div style={{ height: '4px', background: 'var(--glass-border)', borderRadius: '2px' }}>
            <div style={{ width: '75%', height: '100%', background: 'var(--accent-teal)', borderRadius: '2px' }}></div>
          </div>
          <li className="nav-item" style={{ marginTop: 'auto', paddingTop: '2rem', listStyle: 'none' }}>
            <a 
              href="#" 
              className="nav-link"
              style={{ color: '#EF4444' }}
              onClick={async () => {
                if(window.confirm('WARNING: This will permanently delete your account, videos, and interview scores to comply with DPDP/GDPR. Proceed?')) {
                  try {
                    await fetch('http://127.0.0.1:8000/user/data/candidate@audit.ai', { method: 'DELETE' });
                    alert('Data permanently deleted.');
                  } catch (e) {
                    alert('Error deleting data.');
                  }
                }
              }}
            >
              <i className="fas fa-trash-alt"></i> Delete My Data
            </a>
          </li>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;

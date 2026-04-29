import React, { useState, useEffect } from 'react';

const Dashboard = ({ setView }) => {
  const [accessCode, setAccessCode] = useState('');
  const [stats, setStats] = useState({ streak: 0, xp: 0, badges: [] });

  useEffect(() => {
    fetch('http://127.0.0.1:8000/user/stats/candidate@audit.ai')
      .then(res => res.json())
      .then(data => {
        if (!data.detail) setStats(data);
      })
      .catch(err => console.error("Error fetching stats:", err));
  }, []);

  const handleAccessCode = () => {
    if (accessCode.trim().toUpperCase() === 'GOOGLE-2026') {
      alert('Assignment Unlocked: Google Cloud Architecture Assessment');
      setView('practice');
    } else {
      alert('Invalid Access Code. Please check with your mentor.');
    }
  };

  return (
    <section id="view-dashboard" className="animate-fade">
      <header style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2>Your Preparation Dashboard</h2>
        <p>Consistency is the key to success. You've practiced 4 days this week!</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-lg)' }}>
        <div className="glass metric-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <i className="fas fa-fire" style={{ fontSize: '2.5rem', color: '#F59E0B', marginBottom: '0.5rem' }}></i>
          <p style={{ margin: 0, fontWeight: 'bold', fontSize: '1.2rem' }}>{stats.streak} Day Streak!</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Practice tomorrow to keep it alive</p>
        </div>
        <div className="glass metric-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <i className="fas fa-trophy" style={{ fontSize: '2.5rem', color: '#10B981', marginBottom: '0.5rem' }}></i>
          <p style={{ margin: 0, fontWeight: 'bold', fontSize: '1.2rem' }}>{stats.badges.length} Badges Earned</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Top candidate performance</p>
        </div>
        <div className="glass metric-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
          <i className="fas fa-star" style={{ fontSize: '2.5rem', color: '#3B82F6', marginBottom: '0.5rem' }}></i>
          <p style={{ margin: 0, fontWeight: 'bold', fontSize: '1.2rem' }}>{stats.xp.toLocaleString()} XP</p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Keep practicing to level up!</p>
        </div>
      </div>

      <div style={{ marginTop: 'var(--spacing-xl)', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--spacing-lg)' }}>
        <div className="glass" style={{ padding: 'var(--spacing-lg)' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Your Trophy Room 🏆</h3>
          <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2.5rem' }}>
            {stats.badges.length === 0 && <p style={{ color: 'var(--text-secondary)' }}>No badges yet. Start practicing to earn them!</p>}
            {stats.badges.includes('Gold Orator') && (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(255,215,0,0.1)', border: '1px solid #FFD700', borderRadius: '12px', minWidth: '120px' }}>
                <i className="fas fa-award" style={{ fontSize: '2rem', color: '#FFD700', marginBottom: '0.5rem' }}></i>
                <p style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#FFD700' }}>Gold Orator</p>
                <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>&gt;90% Comm Score</p>
              </div>
            )}
            {stats.badges.includes('Silver Architect') && (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(192,192,192,0.1)', border: '1px solid #C0C0C0', borderRadius: '12px', minWidth: '120px' }}>
                <i className="fas fa-medal" style={{ fontSize: '2rem', color: '#C0C0C0', marginBottom: '0.5rem' }}></i>
                <p style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#C0C0C0' }}>Silver Architect</p>
                <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>Passed System Design</p>
              </div>
            )}
            {stats.badges.includes('Ice Breaker') && (
              <div style={{ textAlign: 'center', padding: '1rem', background: 'rgba(59,130,246,0.1)', border: '1px solid #3B82F6', borderRadius: '12px', minWidth: '120px' }}>
                <i className="fas fa-shield-alt" style={{ fontSize: '2rem', color: '#3B82F6', marginBottom: '0.5rem' }}></i>
                <p style={{ fontSize: '0.8rem', fontWeight: 'bold', color: '#3B82F6' }}>Ice Breaker</p>
                <p style={{ fontSize: '0.65rem', color: 'var(--text-secondary)' }}>Survived Roulette</p>
              </div>
            )}
          </div>

          <h3 style={{ marginBottom: '1rem' }}>Recent Activity</h3>
          <div style={{ marginTop: '1rem' }}>
            <div className="course-card glass">
              <i className="fas fa-play-circle" style={{ color: 'var(--accent-teal)' }}></i>
              <div>
                <h4 style={{ margin: 0 }}>Behavioral Interviewing 101</h4>
                <p style={{ fontSize: '0.8rem', margin: 0 }}>Completed 15 mins ago</p>
              </div>
            </div>
            <div className="course-card glass">
              <i className="fas fa-video" style={{ color: 'var(--accent-blue)' }}></i>
              <div>
                <h4 style={{ margin: 0 }}>Mock Interview: Senior SWE</h4>
                <p style={{ fontSize: '0.8rem', margin: 0 }}>Completed yesterday</p>
              </div>
            </div>
          </div>
        </div>
        <div className="glass" style={{ padding: 'var(--spacing-lg)' }}>
          <h3>Next Up</h3>
          <p style={{ marginBottom: '1rem' }}>Recommended for you</p>
          <button className="btn btn-primary" style={{ width: '100%', marginBottom: '1rem' }} onClick={() => setView('roulette')}>
            ⚡ Start Interview Roulette
          </button>
          <button className="btn btn-outline" style={{ width: '100%', marginBottom: '2rem' }}>Mastering Body Language</button>
          
          <h3 style={{ marginTop: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1.5rem' }}>🎓 Mentor Assignments</h3>
          <p style={{ fontSize: '0.85rem', marginBottom: '1rem', color: 'var(--text-secondary)' }}>Have an access code from your instructor or recruiter?</p>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <input 
              type="text" 
              placeholder="e.g. GOOGLE-2026" 
              value={accessCode}
              onChange={(e) => setAccessCode(e.target.value)}
              style={{ flex: 1, padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--glass-border)', background: 'rgba(0,0,0,0.2)', color: 'white' }}
            />
            <button className="btn btn-primary" onClick={handleAccessCode}>Unlock</button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Dashboard;

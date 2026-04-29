import React from 'react';

const MyVideos = () => {
  return (
    <section id="view-my-videos" className="animate-fade">
      <header style={{ marginBottom: 'var(--spacing-lg)' }}>
        <h2>🎥 My Interview Recordings</h2>
        <p>Review your past performances to spot nervous habits and track your improvement.</p>
      </header>

      <div className="glass" style={{ padding: 'var(--spacing-lg)', textAlign: 'center', marginTop: 'var(--spacing-xl)' }}>
        <i className="fas fa-video-slash" style={{ fontSize: '3rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}></i>
        <h3>No Recordings Yet</h3>
        <p style={{ maxWidth: '400px', margin: '0 auto', marginBottom: '1.5rem' }}>
          When you practice in the Mock Interview room, your video recordings will automatically download and be indexed here for self-review.
        </p>
        <button className="btn btn-primary" onClick={() => document.querySelector('[onclick="setCurrentView(\'practice\')"]')?.click()}>
          Start a Mock Interview <i className="fas fa-arrow-right"></i>
        </button>
      </div>

      <div style={{ marginTop: 'var(--spacing-xl)' }}>
        <h3 style={{ marginBottom: '1rem' }}>Demo Replay Structure</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 'var(--spacing-lg)' }}>
          {/* Mock Video Card */}
          <div className="glass" style={{ overflow: 'hidden' }}>
            <div style={{ height: '180px', background: '#000', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
               <i className="fas fa-play-circle" style={{ fontSize: '3rem', color: 'rgba(255,255,255,0.5)', cursor: 'pointer' }}></i>
            </div>
            <div style={{ padding: '1rem' }}>
              <h4 style={{ margin: 0, color: 'var(--accent-teal)' }}>Senior SWE - Behavioral</h4>
              <p style={{ fontSize: '0.8rem', margin: '0.5rem 0' }}>Recorded: Oct 12, 2026</p>
              <div style={{ display: 'flex', gap: '0.5rem', marginTop: '1rem' }}>
                <span className="status-pill" style={{ background: 'rgba(255,215,0,0.1)', color: '#FFD700', padding: '4px 8px', borderRadius: '4px', fontSize: '0.7rem' }}>Gold 🏆</span>
                <span className="status-pill" style={{ background: 'rgba(59,130,246,0.1)', color: '#3B82F6', padding: '4px 8px', borderRadius: '4px', fontSize: '0.7rem' }}>1 Filler Word</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default MyVideos;

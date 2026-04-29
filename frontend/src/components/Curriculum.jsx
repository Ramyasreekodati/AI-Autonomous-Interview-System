import React, { useState } from 'react';

const Curriculum = ({ setView }) => {
  const [activeTrack, setActiveTrack] = useState('fast'); // 'fast' or 'mastery'

  return (
    <section id="view-curriculum" className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h2>📚 Learning Tracks</h2>
          <p>Choose your preparation intensity. Learn the theory before you practice with the AI.</p>
        </div>
      </div>

      {/* Track Selector */}
      <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
        <button 
          className={`btn ${activeTrack === 'fast' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTrack('fast')}
          style={{ flex: 1, padding: '1.5rem' }}
        >
          <h3 style={{ margin: 0 }}><i className="fas fa-bolt" style={{ color: activeTrack === 'fast' ? '#F59E0B' : 'inherit' }}></i> Fast Track</h3>
          <p style={{ fontSize: '0.8rem', margin: '0.5rem 0 0 0', opacity: 0.8 }}>1 Hour • Quick Refresh</p>
        </button>
        <button 
          className={`btn ${activeTrack === 'mastery' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTrack('mastery')}
          style={{ flex: 1, padding: '1.5rem' }}
        >
          <h3 style={{ margin: 0 }}><i className="fas fa-graduation-cap" style={{ color: activeTrack === 'mastery' ? '#10B981' : 'inherit' }}></i> Mastery Track</h3>
          <p style={{ fontSize: '0.8rem', margin: '0.5rem 0 0 0', opacity: 0.8 }}>10 Hours • Deep Dive & Certification</p>
        </button>
      </div>

      {/* Course Content */}
      <div className="glass" style={{ padding: 'var(--spacing-lg)' }}>
        <h3 style={{ marginBottom: '1.5rem' }}>{activeTrack === 'fast' ? 'Fast Track Modules' : 'Mastery Track Modules'}</h3>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '1.5rem' }}>
          
          {/* Module 1 */}
          <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '1.5rem' }}>
            <span style={{ background: 'rgba(16,185,129,0.2)', color: '#10B981', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>MODULE 1</span>
            <h4 style={{ margin: '1rem 0 0.5rem 0' }}>The STAR Method</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Learn how to structure behavioral answers perfectly using Situation, Task, Action, and Result.
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem' }}><i className="fas fa-video"></i> 12 Mins</span>
              <button className="btn btn-outline" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>Watch</button>
            </div>
          </div>

          {/* Module 2 */}
          <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '1.5rem' }}>
            <span style={{ background: 'rgba(59,130,246,0.2)', color: '#3B82F6', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>MODULE 2</span>
            <h4 style={{ margin: '1rem 0 0.5rem 0' }}>{activeTrack === 'fast' ? 'Top 10 Tech Questions' : 'System Design Fundamentals'}</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              {activeTrack === 'fast' 
                ? 'A rapid review of the most common technical questions asked in Indian IT.'
                : 'Deep dive into architecting scalable, distributed systems for FAANG interviews.'}
            </p>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '0.8rem' }}><i className="fas fa-video"></i> {activeTrack === 'fast' ? '15 Mins' : '2 Hours'}</span>
              <button className="btn btn-outline" style={{ padding: '0.4rem 1rem', fontSize: '0.8rem' }}>Watch</button>
            </div>
          </div>

          {/* Module 3 */}
          <div style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '12px', padding: '1.5rem' }}>
            <span style={{ background: 'rgba(245,158,11,0.2)', color: '#F59E0B', padding: '0.2rem 0.6rem', borderRadius: '4px', fontSize: '0.7rem', fontWeight: 'bold' }}>PRACTICE</span>
            <h4 style={{ margin: '1rem 0 0.5rem 0' }}>Apply Your Knowledge</h4>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginBottom: '1rem' }}>
              Put theory into practice by facing the LangGraph AI in a simulated interview environment.
            </p>
            <button className="btn btn-primary" style={{ width: '100%', padding: '0.5rem', fontSize: '0.9rem' }} onClick={() => setView('practice')}>
              Launch AI Mock Interview
            </button>
          </div>

        </div>
      </div>
    </section>
  );
};

export default Curriculum;

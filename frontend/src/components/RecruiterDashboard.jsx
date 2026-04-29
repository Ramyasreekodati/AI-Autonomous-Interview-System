import React, { useState, useEffect } from 'react';

const RecruiterDashboard = () => {
  const [candidates, setCandidates] = useState([]);
  const [interviews, setInterviews] = useState([]);
  const [stats, setStats] = useState({ total_sessions: 0, average_score: 0, total_candidates: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [cRes, iRes, sRes] = await Promise.all([
          fetch('http://127.0.0.1:8000/recruiter/candidates'),
          fetch('http://127.0.0.1:8000/recruiter/interviews'),
          fetch('http://127.0.0.1:8000/recruiter/stats')
        ]);
        setCandidates(await cRes.json());
        setInterviews(await iRes.json());
        setStats(await sRes.json());
      } catch (e) {
        console.error("Failed to fetch recruiter data", e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div className="animate-fade" style={{ padding: '2rem', textAlign: 'center' }}><h2>Loading System Data...</h2></div>;

  return (
    <div className="animate-fade">
      <header style={{ marginBottom: '2rem' }}>
        <h2>🏢 Recruiter Command Center</h2>
        <p>Enterprise-level oversight of all interview sessions and candidate performance.</p>
      </header>

      {/* Global Metrics */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2.5rem' }}>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <p style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.5rem' }}>TOTAL CANDIDATES</p>
          <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--accent-blue)' }}>{stats.total_candidates}</h3>
        </div>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <p style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.5rem' }}>INTERVIEW SESSIONS</p>
          <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--accent-purple)' }}>{stats.total_sessions}</h3>
        </div>
        <div className="glass" style={{ padding: '1.5rem' }}>
          <p style={{ fontSize: '0.8rem', opacity: 0.7, marginBottom: '0.5rem' }}>SYSTEM AVG SCORE</p>
          <h3 style={{ fontSize: '2.5rem', margin: 0, color: 'var(--accent-teal)' }}>{stats.average_score}%</h3>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '1.5rem' }}>
        {/* Recent Interviews Table */}
        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Recent Assessments</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--glass-border)', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                <th style={{ padding: '1rem' }}>ID</th>
                <th style={{ padding: '1rem' }}>START TIME</th>
                <th style={{ padding: '1rem' }}>STATUS</th>
                <th style={{ padding: '1rem' }}>SCORE</th>
                <th style={{ padding: '1rem' }}>RISK</th>
              </tr>
            </thead>
            <tbody>
              {interviews.map(i => (
                <tr key={i.id} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '0.9rem' }}>
                  <td style={{ padding: '1rem' }}>#{i.id}</td>
                  <td style={{ padding: '1rem' }}>{new Date(i.start_time).toLocaleDateString()}</td>
                  <td style={{ padding: '1rem' }}>
                    <span style={{ padding: '0.2rem 0.6rem', borderRadius: '4px', background: i.status === 'completed' ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)', color: i.status === 'completed' ? '#10B981' : '#F59E0B' }}>
                      {i.status.toUpperCase()}
                    </span>
                  </td>
                  <td style={{ padding: '1rem', fontWeight: 'bold' }}>{i.total_score}%</td>
                  <td style={{ padding: '1rem' }}>
                     <span style={{ color: i.risk_level === 'low' ? '#10B981' : i.risk_level === 'medium' ? '#F59E0B' : '#EF4444' }}>
                        ● {i.risk_level.toUpperCase()}
                     </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Candidate List */}
        <div className="glass" style={{ padding: '1.5rem' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>Candidate Pool</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            {candidates.map(c => (
              <div key={c.id} className="course-card glass" style={{ margin: 0 }}>
                <div style={{ width: '40px', height: '40px', background: 'var(--accent-blue)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem', fontWeight: 'bold' }}>
                  {c.name.charAt(0)}
                </div>
                <div>
                  <h4 style={{ margin: 0 }}>{c.name}</h4>
                  <p style={{ fontSize: '0.7rem', margin: 0 }}>{c.email}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default RecruiterDashboard;

import React from 'react';

const Certificate = () => {
  const handleDownload = () => {
    window.print();
  };

  return (
    <section id="view-certificate" className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h2>🎓 Your Certifications</h2>
          <p>Verified achievements from the AI Autonomous Interview System.</p>
        </div>
        <button className="btn btn-primary" onClick={handleDownload}>
          <i className="fas fa-download"></i> Download PDF
        </button>
      </div>

      {/* Certificate Render Area (Printable) */}
      <div 
        id="certificate-container"
        style={{ 
          background: 'linear-gradient(135deg, #0F172A 0%, #1E293B 100%)', 
          border: '10px solid #10B981', 
          borderRadius: '20px', 
          padding: '4rem', 
          textAlign: 'center',
          boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
          position: 'relative',
          overflow: 'hidden',
          maxWidth: '800px',
          margin: '0 auto',
          color: 'white'
        }}
      >
        {/* Decorative Elements */}
        <div style={{ position: 'absolute', top: '-50px', left: '-50px', width: '200px', height: '200px', background: 'rgba(16,185,129,0.1)', borderRadius: '50%' }}></div>
        <div style={{ position: 'absolute', bottom: '-50px', right: '-50px', width: '200px', height: '200px', background: 'rgba(59,130,246,0.1)', borderRadius: '50%' }}></div>
        
        <i className="fas fa-award" style={{ fontSize: '5rem', color: '#10B981', marginBottom: '1.5rem' }}></i>
        
        <h1 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '3rem', margin: '0 0 1rem 0', letterSpacing: '2px', textTransform: 'uppercase', color: '#10B981' }}>
          Certificate of Excellence
        </h1>
        
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '2rem' }}>
          This is proudly presented to
        </p>
        
        <h2 style={{ fontSize: '2.5rem', margin: '0 0 2rem 0', borderBottom: '2px solid rgba(255,255,255,0.2)', paddingBottom: '1rem', display: 'inline-block', minWidth: '400px' }}>
          Candidate Name
        </h2>
        
        <p style={{ fontSize: '1.2rem', color: 'var(--text-secondary)', marginBottom: '1rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
          For successfully completing the <strong>Mastery Track</strong> and demonstrating exceptional technical and behavioral competencies by scoring <strong>&gt;85%</strong> in the AI Autonomous Mock Interview.
        </p>
        
        <div style={{ display: 'flex', justifyContent: 'space-around', marginTop: '3rem', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '2rem' }}>
          <div>
            <p style={{ margin: '0 0 0.5rem 0', fontWeight: 'bold' }}>Oct 12, 2026</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>Date of Completion</p>
          </div>
          <div>
            <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Google_%22G%22_logo.svg/120px-Google_%22G%22_logo.svg.png" alt="Seal" style={{ width: '40px', opacity: 0.5 }} />
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginTop: '0.5rem' }}>AI Verified</p>
          </div>
          <div>
            <p style={{ margin: '0 0 0.5rem 0', fontFamily: 'cursive', fontSize: '1.5rem', color: '#10B981' }}>Antigravity AI</p>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>System Director</p>
          </div>
        </div>
      </div>
      
      {/* Print Styles */}
      <style dangerouslySetInnerHTML={{__html: `
        @media print {
          body * { visibility: hidden; }
          #certificate-container, #certificate-container * { visibility: visible; }
          #certificate-container { position: absolute; left: 0; top: 0; width: 100%; border: none; box-shadow: none; }
        }
      `}} />
    </section>
  );
};

export default Certificate;

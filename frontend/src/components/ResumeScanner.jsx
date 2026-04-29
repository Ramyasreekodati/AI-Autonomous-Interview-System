import React, { useState } from 'react';

const ResumeScanner = () => {
  const [file, setFile] = useState(null);
  const [jobDesc, setJobDesc] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [results, setResults] = useState(null);

  const handleScan = async () => {
    if (!file) {
      alert("Please upload a PDF resume first.");
      return;
    }
    
    setIsScanning(true);
    
    const formData = new FormData();
    formData.append("file", file);
    formData.append("job_desc", jobDesc || "Generic Tech Role");

    try {
      const response = await fetch("http://127.0.0.1:8000/resume/analyze", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Resume scanning failed:", error);
      alert("Failed to connect to AI engine.");
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <section id="view-resume" className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h2>📄 Resume AI Scanner</h2>
          <p>Instantly check your ATS compatibility against real job descriptions.</p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--spacing-lg)' }}>
        {/* Input Panel */}
        <div className="glass" style={{ padding: 'var(--spacing-lg)' }}>
          <h3 style={{ marginBottom: '1rem' }}>1. Upload Your Resume</h3>
          <div style={{ border: '2px dashed rgba(255,255,255,0.2)', padding: '2rem', textAlign: 'center', borderRadius: '12px', marginBottom: '2rem' }}>
            <i className="fas fa-file-pdf" style={{ fontSize: '3rem', color: '#EF4444', marginBottom: '1rem' }}></i>
            <p style={{ marginBottom: '1rem' }}>{file ? file.name : "Drag & Drop or Click to Browse"}</p>
            <input 
              type="file" 
              accept=".pdf" 
              onChange={(e) => setFile(e.target.files[0])} 
              style={{ display: 'block', margin: '0 auto', fontSize: '0.8rem' }}
            />
          </div>

          <h3 style={{ marginBottom: '1rem' }}>2. Target Job Description</h3>
          <textarea 
            placeholder="Paste the LinkedIn/Indeed job description here..."
            style={{ width: '100%', height: '150px', background: 'rgba(0,0,0,0.2)', border: '1px solid rgba(255,255,255,0.1)', color: '#fff', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}
            value={jobDesc}
            onChange={(e) => setJobDesc(e.target.value)}
          ></textarea>

          <button className="btn btn-primary" style={{ width: '100%' }} onClick={handleScan} disabled={isScanning}>
            {isScanning ? "Scanning with AI..." : "🚀 ANALYZE MATCH"}
          </button>
        </div>

        {/* Results Panel */}
        <div className="glass" style={{ padding: 'var(--spacing-lg)' }}>
          <h3 style={{ marginBottom: '1.5rem' }}>AI Match Report</h3>
          
          {!results && !isScanning && (
             <div style={{ textAlign: 'center', color: 'var(--text-secondary)', marginTop: '4rem' }}>
                <i className="fas fa-robot" style={{ fontSize: '4rem', marginBottom: '1rem', opacity: 0.5 }}></i>
                <p>Upload a resume to generate your ATS report.</p>
             </div>
          )}

          {isScanning && (
            <div style={{ textAlign: 'center', marginTop: '4rem' }}>
               <div className="spinner" style={{ width: '40px', height: '40px', border: '4px solid rgba(255,255,255,0.1)', borderTopColor: '#10B981', borderRadius: '50%', animation: 'spin 1s linear infinite', margin: '0 auto 1rem' }}></div>
               <p className="pulse-dot">Parsing structure and cross-referencing keywords...</p>
            </div>
          )}

          {results && !isScanning && (
            <div className="animate-fade">
              <div style={{ display: 'flex', gap: '1rem', marginBottom: '2rem' }}>
                <div style={{ flex: 1, background: 'rgba(16,185,129,0.1)', border: '1px solid #10B981', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.8rem', color: '#10B981', fontWeight: 'bold' }}>ATS Match Score</p>
                  <h1 style={{ margin: 0, color: '#10B981', fontSize: '3rem' }}>{results.ats_keyword_match}%</h1>
                </div>
                <div style={{ flex: 1, background: 'rgba(59,130,246,0.1)', border: '1px solid #3B82F6', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.8rem', color: '#3B82F6', fontWeight: 'bold' }}>Formatting Score</p>
                  <h1 style={{ margin: 0, color: '#3B82F6', fontSize: '3rem' }}>{results.formatting_score}%</h1>
                </div>
              </div>

              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem' }}>
                <h4 style={{ marginBottom: '0.5rem', color: '#F59E0B' }}><i className="fas fa-lightbulb"></i> AI Insight</h4>
                <p style={{ fontSize: '0.9rem' }}>{results.insight}</p>
              </div>

              {results.missing_keywords && results.missing_keywords.length > 0 && (
                <div>
                  <h4 style={{ marginBottom: '0.5rem', color: '#EF4444' }}>Missing Critical Keywords</h4>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {results.missing_keywords.map((kw, i) => (
                      <span key={i} style={{ background: 'rgba(239,68,68,0.2)', color: '#EF4444', padding: '0.3rem 0.6rem', borderRadius: '4px', fontSize: '0.8rem' }}>
                        {kw}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default ResumeScanner;

import React, { useState, useEffect, useRef } from 'react';


const Roulette = ({ setView }) => {
  const [isActive, setIsActive] = useState(false);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [timeLeft, setTimeLeft] = useState(60);
  const [shuffledQuestions, setShuffledQuestions] = useState([]);
  const videoRef = useRef(null);

  // Initialize
  useEffect(() => {
    // Start webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
          if (videoRef.current) videoRef.current.srcObject = stream;
        })
        .catch(err => console.error("Webcam error:", err));
    }
    
    // Fetch dynamic questions from backend
    const fetchQuestions = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/interview/roulette/questions?count=5');
        const data = await response.json();
        if (data.questions && data.questions.length > 0) {
          setShuffledQuestions(data.questions);
        } else {
          // Fallback if data is empty
          setShuffledQuestions(fallbackQuestions);
        }
      } catch (error) {
        console.error("Failed to fetch roulette questions:", error);
        setShuffledQuestions(fallbackQuestions);
      }
    };

    fetchQuestions();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const fallbackQuestions = [
    "Tell me about a time you had to deal with a difficult coworker.",
    "Describe a situation where you failed. What did you learn?",
    "How do you prioritize multiple deadlines?",
    "Tell me about a time you went above and beyond for a project.",
    "How do you handle negative feedback?"
  ];

  // Timer logic
  useEffect(() => {
    let timer = null;
    if (isActive && timeLeft > 0) {
      timer = setInterval(() => {
        setTimeLeft(prev => prev - 1);
      }, 1000);
    } else if (isActive && timeLeft === 0) {
      handleNextQuestion();
    }
    return () => clearInterval(timer);
  }, [isActive, timeLeft]);

  const startRoulette = () => {
    setIsActive(true);
  };

  const handleNextQuestion = async () => {
    if (currentQIndex < 4) {
      setCurrentQIndex(prev => prev + 1);
      setTimeLeft(60); // Reset timer
    } else {
      setIsActive(false);
      
      // Award 'Ice Breaker' badge
      try {
        await fetch('http://127.0.0.1:8000/user/stats/update', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email: "candidate@audit.ai",
            xp_gain: 100,
            badge: "Ice Breaker"
          })
        });
      } catch (e) {
        console.error("Failed to award roulette badge:", e);
      }

      alert("Roulette Complete! You survived the rapid-fire round. +100 XP & 'Ice Breaker' Badge Earned!");
      setView('dashboard');
    }
  };

  return (
    <section id="view-roulette" className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h2>⚡ Interview Roulette</h2>
          <p>Rapid-fire behavioral prep. 5 questions. 60 seconds each. Do not freeze.</p>
        </div>
        <button className="btn btn-outline" onClick={() => setView('dashboard')}>Exit Session</button>
      </div>

      <div className="interview-container" style={{ gridTemplateColumns: '1fr' }}>
        <div className="video-wrapper" style={{ height: '60vh' }}>
          <video ref={videoRef} autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }}></video>
          
          {!isActive && currentQIndex === 0 ? (
            <div className="question-overlay" style={{ background: 'rgba(0,0,0,0.8)', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
              <i className="fas fa-bolt" style={{ fontSize: '4rem', color: '#F59E0B', marginBottom: '1rem' }}></i>
              <h2 style={{ color: 'white', marginBottom: '1rem' }}>Are you ready?</h2>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>You will face 5 rapid-fire questions. You have exactly 60 seconds to answer each.</p>
              <button className="btn btn-primary" onClick={startRoulette} style={{ alignSelf: 'center', fontSize: '1.2rem', padding: '1rem 3rem' }}>
                START ROULETTE
              </button>
            </div>
          ) : (
            <div className="question-overlay">
              <div style={{ position: 'absolute', top: '1rem', right: '2rem', fontSize: '3rem', fontWeight: 'bold', color: timeLeft <= 10 ? '#EF4444' : '#10B981', textShadow: '0 2px 10px rgba(0,0,0,0.5)' }}>
                {timeLeft}s
              </div>
              <h2 className="animate-fade" style={{ fontSize: '2rem', maxWidth: '80%', margin: '0 auto', textShadow: '0 2px 4px rgba(0,0,0,0.8)' }}>
                {shuffledQuestions[currentQIndex]}
              </h2>
              <div style={{ display: 'flex', gap: '1rem', marginTop: '2rem', justifyContent: 'center' }}>
                <span style={{ background: 'rgba(0,0,0,0.5)', padding: '0.5rem 1rem', borderRadius: '20px', color: '#fff' }}>Question {currentQIndex + 1} of 5</span>
                <button className="btn btn-primary" onClick={handleNextQuestion}>Next Question <i className="fas fa-forward"></i></button>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default Roulette;

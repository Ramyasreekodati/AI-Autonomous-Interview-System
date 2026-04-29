import React, { useState, useEffect, useRef } from 'react';

const PracticeRoom = ({ setView }) => {
  const [answer, setAnswer] = useState('');
  const [question, setQuestion] = useState('Connecting to AI Coach...');
  const [metrics, setMetrics] = useState({ pace: 0, conf: 0, fillers: 0 });
  const [coachingTip, setCoachingTip] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [transcript, setTranscript] = useState([]);
  const ws = useRef(null);
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const chunksRef = useRef([]);
  const recognitionRef = useRef(null);
  const canvasRef = useRef(null);
  const [alerts, setAlerts] = useState([]);
  const [emotion, setEmotion] = useState("Neutral");
  const [gaze, setGaze] = useState("Center");

  useEffect(() => {
    // Start webcam
    if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
      navigator.mediaDevices.getUserMedia({ video: true, audio: true })
        .then(stream => {
          if (videoRef.current) videoRef.current.srcObject = stream;
          
          // Setup MediaRecorder
          const mediaRecorder = new MediaRecorder(stream, { mimeType: 'video/webm' });
          mediaRecorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
          };
          mediaRecorder.onstop = () => {
            const blob = new Blob(chunksRef.current, { type: 'video/webm' });
            const url = URL.createObjectURL(blob);
            
            // Auto-download the recording (for MVP local testing)
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `Interview_Session_${new Date().getTime()}.webm`;
            document.body.appendChild(a);
            a.click();
            setTimeout(() => {
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
            }, 100);
            chunksRef.current = [];
          };
          mediaRecorderRef.current = mediaRecorder;
          
          // Start proctoring frame capture
          const captureInterval = setInterval(() => {
            if (!videoRef.current || !canvasRef.current) return;
            const canvas = canvasRef.current;
            const video = videoRef.current;
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;
            canvas.getContext('2d').drawImage(video, 0, 0);
            
            canvas.toBlob(async (blob) => {
              const formData = new FormData();
              formData.append('file', blob, 'frame.jpg');
              try {
                // interview_id is mocked for now as 1 in PracticeRoom
                const res = await fetch(`http://localhost:8000/proctoring/process_frame?interview_id=1`, {
                  method: 'POST',
                  body: formData
                });
                const data = await res.json();
                setAlerts(data.alerts || []);
                setEmotion(data.emotion || "Normal");
                setGaze(data.gaze || "Center");
              } catch (err) {
                console.error("Proctoring sync failed");
              }
            }, 'image/jpeg');
          }, 5000); // Capture every 5 seconds

          return () => clearInterval(captureInterval);
        })
        .catch(err => console.error("Webcam/Mic error:", err));
    }

    // Setup Speech Recognition (Browser Native STT)
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';
      
      recognition.onresult = (event) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setAnswer(currentTranscript);
      };
      
      recognitionRef.current = recognition;
    }

    // Connect WebSocket
    ws.current = new WebSocket('ws://localhost:8000/ws/interview');
    ws.current.onopen = () => console.log('Connected to LangGraph Agent');
    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'state_update') {
        const state = data.state;
        setQuestion(state.current_question);
        setTranscript(state.transcript);
        if (state.coaching_tip) setCoachingTip(state.coaching_tip);
        if (state.scores) {
          setMetrics({
            pace: 140, // Mocked pace for now
            conf: state.scores.overall_grade || 0,
            fillers: state.scores.filler_words || 0,
            badge: state.scores.badge || 'Pending',
            tone: state.scores.tone || 'Neutral'
          });
        }
      }
    };

    return () => {
      if (ws.current) ws.current.close();
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  const submitAnswer = () => {
    if (!answer.trim() || !ws.current) return;
    
    // Add temporary message to UI
    setTranscript(prev => [...prev, { role: 'human', content: answer }]);
    setQuestion("Evaluating your answer and generating next question...");
    
    // Send to LangGraph via WebSocket
    ws.current.send(JSON.stringify({
      type: "human_answer",
      content: answer
    }));
    
    setAnswer('');
  };

  return (
    <section id="view-interview" className="animate-fade">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-md)' }}>
        <div>
          <h2>AI Mock Interview</h2>
          <p>Session: General Behavioral</p>
        </div>
        <button className="btn btn-outline" onClick={() => setView('dashboard')}>Exit Session</button>
      </div>

      <div className="interview-container">
        <div className="video-wrapper">
          <video ref={videoRef} id="webcam-preview" autoPlay muted playsInline style={{ width: '100%', height: '100%', objectFit: 'cover' }}></video>
          <canvas ref={canvasRef} style={{ display: 'none' }} />
          
          {/* Proctoring Alerts Overlay */}
          {alerts.length > 0 && (
            <div style={{ position: 'absolute', top: '1rem', left: '1rem', background: 'rgba(239, 68, 68, 0.8)', padding: '0.5rem 1rem', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '0.5rem', animation: 'pulse-red 2s infinite' }}>
              <i className="fas fa-exclamation-triangle"></i>
              <span style={{ fontSize: '0.8rem', fontWeight: 'bold' }}>{alerts[0].alert_type.replace('_', ' ').toUpperCase()}</span>
            </div>
          )}

          <div className="question-overlay">
            <h3 id="current-question" className="animate-fade">{question}</h3>
            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <span style={{ background: 'rgba(0,0,0,0.5)', padding: '0.2rem 0.8rem', borderRadius: '12px', fontSize: '0.7rem' }}>
                <i className="fas fa-eye"></i> Gaze: {gaze}
              </span>
              <span style={{ background: 'rgba(0,0,0,0.5)', padding: '0.2rem 0.8rem', borderRadius: '12px', fontSize: '0.7rem' }}>
                <i className="fas fa-smile"></i> Emotion: {emotion}
              </span>
            </div>
          </div>
        </div>

        <div className="metrics-panel">
          <div className="glass metric-card">
            <h3>Live Analysis</h3>
            <p style={{ fontSize: '0.8rem' }}>Evaluator Agent Active</p>
          </div>
          {coachingTip && (
            <div className="glass" style={{ padding: '1rem', borderLeft: '4px solid var(--accent-teal)', background: 'rgba(16,185,129,0.1)', textAlign: 'left' }}>
              <p style={{ fontSize: '0.7rem', fontWeight: 'bold', color: 'var(--accent-teal)', marginBottom: '0.2rem', textTransform: 'uppercase' }}>💡 Coach's Tip</p>
              <p style={{ fontSize: '0.8rem', margin: 0, color: '#fff', fontStyle: 'italic', lineHeight: '1.4' }}>"{coachingTip}"</p>
            </div>
          )}
          <div className="glass metric-card">
            <p>Speaking Pace</p>
            <div className="metric-value" id="metric-pace">{metrics.pace} WPM</div>
            <p style={{ fontSize: '0.7rem', color: 'var(--accent-teal)' }}>Optimal Range</p>
          </div>
          <div className="glass metric-card">
            <p>Grade / Confidence</p>
            <div className="metric-value" id="metric-conf" style={{ color: 'var(--accent-blue)' }}>{Math.round(metrics.conf)}%</div>
            <p style={{ fontSize: '0.9rem', fontWeight: 'bold', marginTop: '0.2rem' }}>{metrics.badge}</p>
          </div>
          <div className="glass metric-card">
            <p>Filler Words & Tone</p>
            <div className="metric-value" id="metric-fillers" style={{ color: 'var(--accent-purple)' }}>{metrics.fillers}</div>
            <p style={{ fontSize: '0.75rem', marginTop: '0.2rem' }}>Tone: {metrics.tone}</p>
          </div>
          <div className="glass metric-card">
            <p>Transcript</p>
            <div style={{ maxHeight: '150px', overflowY: 'auto', textAlign: 'left', fontSize: '0.8rem', marginTop: '0.5rem' }}>
              {transcript.slice(-4).map((msg, i) => (
                <div key={i} style={{ marginBottom: '0.5rem', color: msg.role === 'ai' ? 'var(--accent-teal)' : '#fff' }}>
                  <strong>{msg.role === 'ai' ? 'AI: ' : 'You: '}</strong>
                  {msg.content.substring(0, 50)}...
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="glass" style={{ marginTop: 'var(--spacing-md)', padding: 'var(--spacing-md)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', flexWrap: 'wrap', gap: '0.5rem' }}>
          <h4 style={{ color: 'var(--text-primary)' }}><i className="fas fa-keyboard"></i> Your Answer</h4>
          <div style={{ display: 'flex', gap: '0.5rem' }}>
            <button className="btn btn-outline" onClick={() => {
              const nextState = !isRecording;
              setIsRecording(nextState);
              if (nextState) {
                chunksRef.current = [];
                setAnswer(''); // Clear previous answer
                if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'inactive') {
                  mediaRecorderRef.current.start(1000); // collect 1s chunks
                }
                if (recognitionRef.current) {
                  try { recognitionRef.current.start(); } catch(e){}
                }
              } else {
                if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
                  mediaRecorderRef.current.stop();
                }
                if (recognitionRef.current) {
                  recognitionRef.current.stop();
                }
              }
            }}>
              <i className="fas fa-microphone" style={{ color: isRecording ? 'red' : 'inherit' }}></i> 
              {isRecording ? 'Stop Recording' : 'Record & Transcribe'}
            </button>
            <button className="btn btn-primary" onClick={submitAnswer}>Submit <i className="fas fa-paper-plane"></i></button>
          </div>
        </div>
        <textarea 
          placeholder="Type your answer here, or click Record to speak..." 
          style={{ width: '100%', minHeight: '110px', background: 'rgba(255,255,255,0.05)', border: '1px solid var(--glass-border)', borderRadius: '12px', padding: '1rem', color: 'var(--text-primary)', fontFamily: "'Outfit', sans-serif", fontSize: '1rem', resize: 'vertical', outline: 'none' }}
          value={answer}
          onChange={(e) => setAnswer(e.target.value)}
        ></textarea>
      </div>
    </section>
  );
};

export default PracticeRoom;

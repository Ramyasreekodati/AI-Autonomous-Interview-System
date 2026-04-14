import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Mic, Video, AlertCircle, CheckCircle } from 'lucide-react';
import axios from 'axios';

const Interview = () => {
  const { id: interviewId } = useParams();
  const navigate = useNavigate();
  const [question, setQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [answer, setAnswer] = useState('');
  const [surveillanceStatus, setSurveillanceStatus] = useState('Active');
  const [alerts, setAlerts] = useState([]);
  const [currentEmotion, setCurrentEmotion] = useState('Neutral');
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    fetchNextQuestion();
    startCamera();
    const interval = setInterval(captureFrame, 3000); // Capture every 3 seconds
    return () => clearInterval(interval);
  }, []);

  const captureFrame = async () => {
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
        const response = await axios.post(`http://localhost:8000/proctoring/process_frame?interview_id=${interviewId}`, formData);
        setAlerts(response.data.alerts);
        setCurrentEmotion(response.data.emotion);
      } catch (err) {
        console.error("Proctoring error", err);
      }
    }, 'image/jpeg');
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch (err) {
      console.error("Camera access denied", err);
    }
  };

  const fetchNextQuestion = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/interview/${interviewId}/next-question`);
      if (response.data.finished) {
        navigate(`/dashboard/${interviewId}`);
      } else {
        setQuestion(response.data);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    try {
      await axios.post(`http://localhost:8000/interview/${interviewId}/submit-response`, null, {
        params: { question_id: question.question_id, answer_text: answer }
      });
      setAnswer('');
      fetchNextQuestion();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="px-8 py-4 border-b border-border flex justify-between items-center glass">
        <h2 className="text-xl font-bold gradient-text">RecruitAI Session</h2>
        <div className="flex gap-4 items-center">
          <span className="flex items-center gap-2 text-sm text-accent">
            <CheckCircle className="w-4 h-4" /> Proctoring Live
          </span>
          <span className="text-sm text-text-muted">Interview ID: {interviewId}</span>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-8 p-8 overflow-hidden">
        {/* Left: AI Monitor & Camera */}
        <div className="flex flex-col gap-6">
          <div className="glass-card flex-1 relative overflow-hidden p-0 rounded-2xl bg-black">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className="w-full h-full object-cover rounded-2xl"
            />
            <canvas ref={canvasRef} className="hidden" />
            <div className="absolute top-4 left-4 bg-red-500/80 px-3 py-1 rounded-full text-xs font-bold flex items-center gap-2 animate-pulse">
              <div className="w-2 h-2 bg-white rounded-full"></div> REC LIVE
            </div>
            
            <div className="absolute top-16 left-4 flex flex-col gap-2">
              {alerts.map((alert, i) => (
                <div key={i} className="bg-error/90 text-white text-[10px] px-2 py-1 rounded-md shadow-lg flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" /> {alert.type.replace(/_/g, ' ')}
                </div>
              ))}
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex gap-4">
              <div className="glass p-3 rounded-xl flex-1 border border-white/10 backdrop-blur-md">
                <p className="text-xs text-text-muted uppercase mb-1">Attention Score</p>
                <div className="w-full bg-white/10 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-primary h-full w-[85%]" />
                </div>
              </div>
              <div className="glass p-3 rounded-xl flex-1 border border-white/10 backdrop-blur-md">
                <p className="text-xs text-text-muted uppercase mb-1">Emotion Detect</p>
                <p className="text-sm font-bold text-accent">{currentEmotion}</p>
              </div>
            </div>
          </div>
          
          <div className="glass-card h-32 flex items-center gap-6 overflow-x-auto">
             <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center text-primary mb-2">
                    <Mic className="w-6 h-6" />
                </div>
                <span className="text-xs text-text-muted">Audio</span>
             </div>
             <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-secondary/20 flex items-center justify-center text-secondary mb-2">
                    <Video className="w-6 h-6" />
                </div>
                <span className="text-xs text-text-muted">Vision</span>
             </div>
             <div className="border-l border-border h-12 ml-4 pl-8">
                <p className="text-xs text-text-muted mb-1">System Status</p>
                <p className="text-sm text-accent flex items-center gap-1 font-mono">
                    ONLINE: AI ENGINE V2.1
                </p>
             </div>
          </div>
        </div>

        {/* Right: Question & Input */}
        <div className="flex flex-col gap-6">
          <AnimatePresence mode="wait">
            {!loading && question && (
              <motion.div 
                key={question.question_id}
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: -20 }}
                className="glass-card flex-1 flex flex-col"
              >
                <div className="mb-8">
                  <span className="bg-primary/20 text-primary text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">
                    Task Analysis
                  </span>
                  <h3 className="text-2xl font-bold mt-4 leading-relaxed">
                    {question.text}
                  </h3>
                </div>

                <div className="flex-1">
                  <textarea 
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    className="w-full h-full min-h-[200px] bg-surface-light border border-border rounded-xl p-6 focus:ring-2 focus:ring-primary focus:outline-none resize-none transition-all placeholder:text-white/10"
                    placeholder="Speak your answer or type here..."
                  />
                </div>

                <div className="mt-8 flex justify-end gap-4">
                  <button 
                    onClick={handleSubmit} 
                    className="btn-primary px-10 py-4 text-lg"
                  >
                    Submit Response
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <div className="glass-card p-4 border-l-4 border-error/50 flex items-center gap-4">
             <div className="bg-error/20 p-2 rounded-lg text-error">
                <AlertCircle className="w-6 h-6" />
             </div>
             <div>
                <p className="text-sm font-bold">Proctoring Notice</p>
                <p className="text-xs text-text-muted">Avoid using external devices or looking away from the camera for extended periods.</p>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Interview;

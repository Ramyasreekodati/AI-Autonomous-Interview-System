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
    <div className="flex flex-col h-screen bg-slate-50">
      {/* Header */}
      <header className="px-8 py-4 bg-white border-b border-slate-200 flex justify-between items-center sticky top-0 z-10">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center">
            <Video className="text-white w-5 h-5" />
          </div>
          <h2 className="text-xl font-bold text-slate-900">Session <span className="text-indigo-600">RecruitAI</span></h2>
        </div>
        <div className="flex gap-6 items-center">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-emerald-50 rounded-lg text-emerald-700 text-xs font-bold border border-emerald-100">
            <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse" />
            SECURE LIVE FEED
          </div>
          <span className="text-sm font-semibold text-slate-400">ID: {interviewId}</span>
        </div>
      </header>

      <main className="flex-1 grid grid-cols-1 lg:grid-cols-12 gap-8 p-8 overflow-hidden">
        {/* Left: AI Monitor & Camera (4 cols) */}
        <div className="lg:col-span-4 flex flex-col gap-6">
          <div className="video-container flex-1">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className="w-full h-full object-cover grayscale-[0.2]"
            />
            <canvas ref={canvasRef} className="hidden" />
            
            <div className="absolute top-4 left-4 flex flex-col gap-2">
              {alerts.length > 0 && alerts.map((alert, i) => (
                <motion.div 
                  initial={{ x: -20, opacity: 0 }}
                  animate={{ x: 0, opacity: 1 }}
                  key={i} 
                  className="bg-rose-500 text-white text-[10px] font-bold px-2.5 py-1.5 rounded-lg shadow-xl flex items-center gap-2 border border-rose-400"
                >
                  <AlertCircle className="w-3.5 h-3.5" /> {alert.type.replace(/_/g, ' ').toUpperCase()}
                </motion.div>
              ))}
            </div>

            <div className="absolute bottom-4 left-4 right-4 flex gap-3">
              <div className="bg-black/60 backdrop-blur-md p-3 rounded-xl flex-1 border border-white/10">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Attention</p>
                <div className="w-full bg-white/20 h-1.5 rounded-full overflow-hidden">
                  <div className="bg-indigo-400 h-full w-[85%] transition-all duration-500" />
                </div>
              </div>
              <div className="bg-black/60 backdrop-blur-md p-3 rounded-xl flex-1 border border-white/10">
                <p className="text-[10px] text-slate-400 font-bold uppercase tracking-wider mb-1">Emotion</p>
                <p className="text-sm font-bold text-white uppercase tracking-tight">{currentEmotion}</p>
              </div>
            </div>
          </div>
          
          <div className="premium-card p-6 flex flex-col gap-4">
             <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400">
                      <Mic className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900 uppercase tracking-wider">Audio Feed</p>
                    <p className="text-[10px] font-medium text-emerald-500">OPTIMIZED</p>
                  </div>
                </div>
                <div className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
             </div>
             <div className="h-px bg-slate-100" />
             <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-slate-50 flex items-center justify-center text-slate-400">
                      <Video className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="text-xs font-bold text-slate-900 uppercase tracking-wider">Vision Engine</p>
                    <p className="text-[10px] font-medium text-indigo-500">ACTIVE V2.0</p>
                  </div>
                </div>
                <div className="w-1.5 h-1.5 rounded-full bg-indigo-500" />
             </div>
          </div>
        </div>

        {/* Right: Question & Input (8 cols) */}
        <div className="lg:col-span-8 flex flex-col gap-6">
          <AnimatePresence mode="wait">
            {!loading && question && (
              <motion.div 
                key={question.question_id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="premium-card flex-1 flex flex-col"
              >
                <div className="mb-8">
                  <div className="inline-flex items-center gap-2 px-2.5 py-1 bg-indigo-50 text-indigo-700 text-[10px] font-extrabold uppercase tracking-widest rounded-md border border-indigo-100">
                    Question Evaluation
                  </div>
                  <h3 className="text-2xl font-bold text-slate-900 mt-6 leading-relaxed">
                    {question.text}
                  </h3>
                </div>

                <div className="flex-1">
                  <textarea 
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                    className="input-field h-full min-h-[300px] text-lg leading-relaxed resize-none border-0 shadow-none bg-slate-50/50 p-6 focus:bg-white"
                    placeholder="Provide your comprehensive response here..."
                  />
                </div>

                <div className="mt-8 flex items-center justify-between">
                  <p className="text-xs font-medium text-slate-400">
                    Characters: {answer.length}
                  </p>
                  <button 
                    onClick={handleSubmit} 
                    disabled={!answer.trim()}
                    className="btn-primary px-10 py-4 shadow-xl disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Submit Response
                    <CheckCircle className="w-5 h-5" />
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          
          <div className="premium-card p-5 border-l-4 border-l-rose-500 flex items-center gap-4 bg-rose-50/30">
             <div className="bg-rose-100 p-2 rounded-xl text-rose-600">
                <AlertCircle className="w-5 h-5" />
             </div>
             <div>
                <p className="text-xs font-extrabold text-slate-900 uppercase tracking-wider">Integrity Watch</p>
                <p className="text-xs font-medium text-slate-500">Ensure a quiet environment for the duration of the evaluation.</p>
             </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default Interview;

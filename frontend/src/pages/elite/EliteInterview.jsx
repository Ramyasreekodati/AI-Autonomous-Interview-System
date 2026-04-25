import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  Square, 
  ChevronRight, 
  ChevronLeft, 
  Shield, 
  Activity, 
  AlertCircle,
  Brain,
  Video,
  X,
  Loader2
} from 'lucide-react';

const EliteInterview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  
  // Existing Logic States
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [questionData, setQuestionData] = useState(null);
  const [answer, setAnswer] = useState("");
  const [error, setError] = useState("");
  
  // Media State
  const [isRecording, setIsRecording] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // Proctoring Metrics (Simulated + Logic)
  const [emotion, setEmotion] = useState("Neutral");
  const [gaze, setGaze] = useState("Center");
  const [pace, setPace] = useState(145);

  useEffect(() => {
    fetchQuestion(0);
    startCamera();
    return () => stopCamera();
  }, [id]);

  const fetchQuestion = async (index) => {
    setLoading(true);
    try {
      const response = await axios.get(`http://localhost:8000/interview/${id}/question/${index}`);
      if (response.data.finished) {
        navigate(`/result/${id}`);
        return;
      }
      setQuestionData(response.data);
      setQuestionIndex(index);
    } catch (err) {
      setError("Failed to sync with AI Engine.");
    } finally {
      setLoading(false);
    }
  };

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) videoRef.current.srcObject = stream;
    } catch (err) {
      console.warn("Camera/Mic access denied");
    }
  };

  const stopCamera = () => {
    if (videoRef.current?.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    }
  };

  const handleNext = async () => {
    setSubmitting(true);
    // Simulate API call for demonstration, but you can integrate real axios.post here
    setTimeout(() => {
      fetchQuestion(questionIndex + 1);
      setSubmitting(false);
    }, 1000);
  };

  if (loading) return (
    <div className="min-h-screen bg-[#0F172A] flex flex-col items-center justify-center text-white font-['Outfit']">
      <Brain className="w-16 h-16 text-[#10B981] animate-pulse mb-6" />
      <h2 className="text-2xl font-bold tracking-tight">Initializing Elite AI Suite...</h2>
      <p className="text-slate-500 mt-2 text-sm">Calibrating proctoring sensors and loading questions</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#0F172A] text-slate-100 font-['Outfit'] p-8">
      {/* Header */}
      <header className="flex justify-between items-center max-w-7xl mx-auto mb-10">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-white/5 flex items-center justify-center border border-white/10">
            <Brain className="text-[#10B981] w-6 h-6" />
          </div>
          <div>
            <h2 className="text-xl font-bold">Elite Mock Session</h2>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest">Question {questionIndex + 1} of {questionData?.total || 10}</p>
          </div>
        </div>
        
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/20 rounded-full">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[10px] font-bold text-emerald-400 uppercase">Live Analysis Active</span>
          </div>
          <button 
            onClick={() => navigate('/')}
            className="p-2 bg-white/5 rounded-full border border-white/10 hover:bg-white/10 transition-all"
          >
            <X size={20} />
          </button>
        </div>
      </header>

      <div className="max-w-7xl mx-auto grid grid-cols-1 lg:grid-cols-3 gap-8 h-[calc(100vh-180px)]">
        {/* Main Content Area */}
        <div className="lg:col-span-2 flex flex-col gap-6">
          <div className="relative flex-grow bg-black rounded-3xl overflow-hidden border border-white/10 shadow-2xl group">
            <video 
              ref={videoRef} 
              autoPlay 
              playsInline 
              muted 
              className="w-full h-full object-cover"
            />
            
            {/* Question Overlay */}
            <div className="absolute bottom-0 left-0 right-0 p-8 bg-gradient-to-t from-black/90 via-black/40 to-transparent">
              <AnimatePresence mode='wait'>
                <motion.h3 
                  key={questionIndex}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  className="text-2xl md:text-3xl font-bold text-white mb-6 leading-tight drop-shadow-lg"
                >
                  {questionData?.text || "Please wait while we load the question..."}
                </motion.h3>
              </AnimatePresence>
              
              <div className="flex justify-between items-center">
                <button 
                  onClick={handleNext}
                  disabled={submitting}
                  className="bg-white text-black font-bold px-8 py-4 rounded-2xl flex items-center gap-2 hover:bg-slate-200 transition-all disabled:opacity-50"
                >
                  {submitting ? <Loader2 className="animate-spin" /> : "Next Question"} <ChevronRight size={18} />
                </button>
                
                <div className="flex items-center gap-4">
                   <div className="text-center px-4">
                      <p className="text-[8px] text-slate-400 uppercase tracking-widest font-bold">Emotion</p>
                      <p className="text-sm font-bold text-[#10B981]">{emotion}</p>
                   </div>
                   <div className="w-[1px] h-8 bg-white/10" />
                   <div className="text-center px-4">
                      <p className="text-[8px] text-slate-400 uppercase tracking-widest font-bold">Gaze</p>
                      <p className="text-sm font-bold text-[#3B82F6]">{gaze}</p>
                   </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Sidebar Metrics */}
        <div className="flex flex-col gap-4 overflow-y-auto pr-2">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6">
            <h4 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-6 flex items-center gap-2">
              <Activity size={14} className="text-[#10B981]" /> Live Analysis
            </h4>
            
            <div className="space-y-6">
              <MetricItem label="Speaking Pace" value={`${pace} WPM`} color="#10B981" subtext="Optimal Range" />
              <MetricItem label="Confidence" value="88%" color="#3B82F6" subtext="Stable Eye Contact" />
              <MetricItem label="Filler Words" value="2" color="#8B5CF6" subtext="Excellent Flow" />
            </div>
          </div>

          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-6">
            <h4 className="text-sm font-bold uppercase tracking-widest text-slate-400 mb-4 flex items-center gap-2">
              <Shield size={14} className="text-indigo-400" /> Proctored Session
            </h4>
            <div className="p-4 bg-emerald-500/5 border border-emerald-500/10 rounded-2xl">
              <p className="text-xs text-slate-300 leading-relaxed">
                AI sensors are monitoring environmental noise and visual stability. No issues detected.
              </p>
            </div>
          </div>

          <div className="mt-auto bg-gradient-to-br from-[#10B981]/20 to-transparent border border-[#10B981]/20 rounded-3xl p-6">
            <h4 className="font-bold text-white mb-2 flex items-center gap-2">
              <Brain size={18} className="text-[#10B981]" /> AI Tip
            </h4>
            <p className="text-xs text-[#10B981] font-medium leading-relaxed">
              Try to maintain a consistent speed. Your pace is currently perfect for clarity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

const MetricItem = ({ label, value, color, subtext }) => (
  <div>
    <div className="flex justify-between items-end mb-2">
      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">{label}</span>
      <span className="text-xl font-bold" style={{ color }}>{value}</span>
    </div>
    <div className="h-1 bg-white/5 rounded-full overflow-hidden mb-1">
      <div className="h-full" style={{ width: '70%', backgroundColor: color }} />
    </div>
    <p className="text-[8px] font-bold text-slate-500 uppercase tracking-widest text-right">{subtext}</p>
  </div>
);

export default EliteInterview;

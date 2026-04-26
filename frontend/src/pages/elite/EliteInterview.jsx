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
    fetchQuestion(true);
    startCamera();
    return () => stopCamera();
  }, [id]);

  const fetchQuestion = async (isFirst = false) => {
    setLoading(true);
    setError("");
    try {
      let response;
      if (isFirst) {
        response = await axios.get(`http://localhost:8000/interview/${id}/question/0`);
      } else {
        response = await axios.get(`http://localhost:8000/interview/${id}/next-question`);
      }

      if (response.data.finished) {
        navigate(`/result/${id}`);
        return;
      }
      setQuestionData(response.data);
      setQuestionIndex(prev => isFirst ? 0 : prev + 1);
      setAnswer("");
      
      // Speak the question
      speakQuestion(response.data.text);
    } catch (err) {
      setError("Failed to sync with AI Engine.");
    } finally {
      setLoading(false);
    }
  };

  const speakQuestion = (text) => {
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.9;
    utterance.pitch = 1;
    window.speechSynthesis.speak(utterance);
  };

  const startRecording = async () => {
    try {
      const stream = videoRef.current.srcObject;
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      
      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) audioChunksRef.current.push(event.data);
      };
      
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await submitAudio(audioBlob);
      };
      
      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      console.error("Recording failed to start", err);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current.stop();
    setIsRecording(false);
  };

  const submitAudio = async (blob) => {
    setSubmitting(true);
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    try {
      const response = await axios.post(
        `http://localhost:8000/interview/${id}/submit-audio?question_id=${questionData.question_id}`, 
        formData
      );
      setAnswer(response.data.transcription);
    } catch (err) {
      setError("AI Transcription failed.");
    } finally {
      setSubmitting(false);
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
    if (!answer.trim() && isRecording) {
      stopRecording();
      return;
    }
    if (!answer.trim()) return;
    
    setSubmitting(true);
    try {
      await axios.post(`http://localhost:8000/interview/${id}/submit-response`, null, {
        params: { question_id: questionData.question_id, answer_text: answer }
      });
      fetchQuestion(false);
    } catch (err) {
      setError("Submission failed.");
    } finally {
      setSubmitting(false);
    }
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
              className="w-full h-full object-cover scale-x-[-1]"
            />
            
            {/* AI Streaming Avatar (New Feature from YouTube guides) */}
            <div className="absolute top-8 right-8 z-30">
               <motion.div 
                 initial={{ opacity: 0, x: 20 }}
                 animate={{ opacity: 1, x: 0 }}
                 className="w-48 h-64 bg-slate-800/80 backdrop-blur-xl border border-white/20 rounded-2xl overflow-hidden shadow-2xl"
               >
                  <div className="h-full w-full bg-gradient-to-br from-indigo-900 to-slate-900 flex flex-col items-center justify-center p-4">
                     <div className="w-20 h-20 bg-indigo-500/20 rounded-full flex items-center justify-center mb-4 ring-2 ring-indigo-500/50">
                        <Brain className="text-indigo-400 w-10 h-10 animate-pulse" />
                     </div>
                     <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest text-center">AI Interviewer</p>
                     <p className="text-xs font-bold text-white text-center mt-1">SARA-1</p>
                     <div className="mt-4 flex gap-1 items-center">
                        <div className="w-1 h-3 bg-indigo-500 animate-bounce" style={{ animationDelay: '0s' }}></div>
                        <div className="w-1 h-5 bg-indigo-400 animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-1 h-2 bg-indigo-600 animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                     </div>
                  </div>
               </motion.div>
            </div>

            {/* Answer Builder Overlay */}
            <div className="absolute top-8 left-8 z-20">
               <div className="glass p-4 w-64">
                  <h4 className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest mb-2 flex items-center gap-2">
                    <Activity size={10} /> Answer Builder
                  </h4>
                  <div className="space-y-1">
                    <div className="flex justify-between items-center bg-white/5 p-2 rounded-lg text-[9px]">
                      <span>Situation</span> <CheckCircle size={10} className="text-emerald-500" />
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-2 rounded-lg text-[9px]">
                      <span>Task</span> <CheckCircle size={10} className="text-emerald-500" />
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-2 rounded-lg text-[9px]">
                      <span>Action</span> <Activity size={10} className="text-indigo-400 animate-pulse" />
                    </div>
                    <div className="flex justify-between items-center bg-white/5 p-2 rounded-lg text-[9px] opacity-40">
                      <span>Result</span> <div className="w-2 h-2 rounded-full bg-white/20" />
                    </div>
                  </div>
               </div>
            </div>

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

              {/* Live Transcript Display */}
              {answer && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="mb-6 p-4 bg-white/10 backdrop-blur-md rounded-2xl border border-white/10 text-sm text-slate-200 line-clamp-2"
                >
                  <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest block mb-1">Transcript Preview</span>
                  {answer}
                </motion.div>
              )}
              
              <div className="flex justify-between items-center">
                <div className="flex gap-4">
                  <button 
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`px-8 py-4 rounded-2xl font-bold flex items-center gap-2 transition-all ${isRecording ? 'bg-red-500 text-white animate-pulse' : 'bg-white/10 text-white hover:bg-white/20'}`}
                  >
                    {isRecording ? <Square size={18} fill="white" /> : <Mic size={18} />}
                    {isRecording ? "Stop Recording" : "Speak Answer"}
                  </button>
                  <button 
                    onClick={handleNext}
                    disabled={submitting || (!answer && !isRecording)}
                    className="bg-white text-black font-bold px-10 py-4 rounded-2xl flex items-center gap-2 hover:bg-slate-200 transition-all disabled:opacity-50"
                  >
                    {submitting ? <Loader2 className="animate-spin" /> : "Next Question"} <ChevronRight size={18} />
                  </button>
                </div>
                
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

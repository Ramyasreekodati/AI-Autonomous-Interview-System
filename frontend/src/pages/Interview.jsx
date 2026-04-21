import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  Type, 
  ChevronLeft, 
  ChevronRight, 
  Loader2,
  AlertCircle,
  Clock,
  CheckCircle2,
  Square,
  Shield,
  Eye,
  Activity
} from 'lucide-react';

const Interview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [questionData, setQuestionData] = useState(null);
  const [answer, setAnswer] = useState("");
  const [inputMode, setInputMode] = useState("text");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  
  // Audio State
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  // 🛡️ Proctoring State
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [proctoringActive, setProctoringActive] = useState(false);
  const [alerts, setAlerts] = useState([]);
  const [emotion, setEmotion] = useState("Normal");
  const [gaze, setGaze] = useState("Center");

  useEffect(() => {
    fetchQuestion(0);
    startProctoring();
    return () => {
      stopProctoring();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [id]);

  const fetchQuestion = async (index) => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const response = await axios.get(`http://localhost:8000/interview/${id}/question/${index}`);
      if (response.data.finished) {
        navigate(`/result/${id}`);
        return;
      }
      setQuestionData(response.data);
      setAnswer(response.data.previous_answer || "");
      setQuestionIndex(index);
    } catch (err) {
      setError("Connectivity issue. Ensure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  // 🛡️ Proctoring Logic
  const startProctoring = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setProctoringActive(true);
        // Start capture loop (every 3 seconds to save bandwidth/quota)
        const interval = setInterval(captureFrame, 3000);
        return () => clearInterval(interval);
      }
    } catch (err) {
      console.warn("Camera access denied - Proctoring offline");
    }
  };

  const stopProctoring = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(t => t.stop());
    }
  };

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
        const res = await axios.post(`http://localhost:8000/proctoring/process_frame?interview_id=${id}`, formData);
        setAlerts(res.data.alerts || []);
        setEmotion(res.data.emotion || "Normal");
        setGaze(res.data.gaze || "Center");
      } catch (err) {
        console.error("Proctoring sync failed");
      }
    }, 'image/jpeg');
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];
      mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
      mediaRecorderRef.current.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        await handleAudioUpload(audioBlob);
        stream.getTracks().forEach(t => t.stop());
      };
      mediaRecorderRef.current.start();
      setIsRecording(true);
      timerRef.current = setInterval(() => setRecordingTime(p => p + 1), 1000);
    } catch (err) {
      setError("Mic error.");
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const handleAudioUpload = async (blob) => {
    setSubmitting(true);
    const formData = new FormData();
    formData.append('file', blob, 'recording.wav');
    try {
      const response = await axios.post(
        `http://localhost:8000/interview/${id}/submit-audio?question_id=${questionData.question_id}`, 
        formData
      );
      setAnswer(response.data.transcription);
      setSuccess("Voice transcribed.");
    } catch (err) {
      setError("AI Transcription failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePrevious = () => {
    if (questionIndex > 0) fetchQuestion(questionIndex - 1);
  };

  const handleNext = async () => {
    if (!answer.trim()) {
      setError("Please provide an answer.");
      return;
    }
    setSubmitting(true);
    try {
      await axios.post(`http://localhost:8000/interview/${id}/submit-response`, null, {
        params: { question_id: questionData.question_id, answer_text: answer }
      });
      fetchQuestion(questionIndex + 1);
    } catch (err) {
      setError("Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div className="min-h-screen flex items-center justify-center bg-slate-950 text-white">Initializing AI Engine...</div>;

  const progress = questionData ? ((questionIndex + 1) / questionData.total) * 100 : 0;

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 text-slate-200">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* MAIN PANEL */}
        <div className="lg:col-span-3 space-y-8">
          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-8 backdrop-blur-xl">
            <div className="mb-6 flex justify-between items-center">
              <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Question {questionIndex + 1} of {questionData.total}</span>
              <div className="flex items-center gap-2 text-xs font-medium text-emerald-400">
                <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
                Live Audit Active
              </div>
            </div>
            <h1 className="text-3xl font-bold text-white mb-10 leading-snug">{questionData.text}</h1>
            
            <div className="space-y-4">
               <div className="flex items-center gap-4 mb-4">
                  <button onClick={() => setInputMode("text")} className={`px-4 py-2 rounded-full text-xs font-bold ${inputMode === "text" ? "bg-indigo-500 text-white" : "bg-white/5 text-white/40"}`}>Keyboard</button>
                  <button onClick={() => setInputMode("audio")} className={`px-4 py-2 rounded-full text-xs font-bold ${inputMode === "audio" ? "bg-indigo-500 text-white" : "bg-white/5 text-white/40"}`}>Voice AI</button>
               </div>

               {inputMode === "text" ? (
                 <textarea 
                    className="w-full bg-slate-950/50 border border-white/5 rounded-2xl p-6 text-lg min-h-[300px] outline-none focus:border-indigo-500/50 transition-colors"
                    placeholder="Type your technical response here..."
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                 />
               ) : (
                 <div className="h-[300px] bg-slate-950/50 border border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center">
                    <button 
                      onClick={isRecording ? stopRecording : startRecording}
                      className={`w-20 h-20 rounded-full flex items-center justify-center transition-all ${isRecording ? "bg-red-500/20 border-red-500" : "bg-indigo-500/20 border-indigo-500"} border`}
                    >
                      {isRecording ? <Square className="fill-red-500 text-red-500" /> : <Mic className="text-indigo-500" />}
                    </button>
                    <p className="mt-4 font-bold">{isRecording ? "Recording..." : "Click to Speak"}</p>
                 </div>
               )}
            </div>

            <div className="mt-10 flex justify-between">
              <button onClick={handlePrevious} disabled={questionIndex === 0} className="px-6 py-3 text-white/40 font-bold hover:text-white disabled:opacity-0 transition-colors flex items-center gap-2"><ChevronLeft /> Back</button>
              <button onClick={handleNext} disabled={submitting} className="px-8 py-3 bg-indigo-600 rounded-xl font-bold text-white hover:bg-indigo-500 transition-colors flex items-center gap-2">
                {submitting ? <Loader2 className="animate-spin" /> : "Commit & Continue"} <ChevronRight />
              </button>
            </div>
          </div>
        </div>

        {/* PROCTORING SIDEBAR */}
        <div className="space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
            <div className="flex items-center gap-2 mb-4">
              <Shield className="text-indigo-400 w-4 h-4" />
              <h3 className="font-bold text-sm uppercase tracking-widest text-white">Surveillance</h3>
            </div>
            
            <div className="aspect-video bg-black rounded-xl mb-4 overflow-hidden relative">
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover grayscale" />
              <canvas ref={canvasRef} className="hidden" />
              <div className="absolute top-2 right-2 bg-red-500 text-[8px] font-black px-1.5 py-0.5 rounded animate-pulse">REC</div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4">
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <p className="text-[8px] font-bold text-white/40 uppercase mb-1">Emotion</p>
                <p className="text-xs font-bold text-white">{emotion}</p>
              </div>
              <div className="bg-white/5 p-3 rounded-xl border border-white/5">
                <p className="text-[8px] font-bold text-white/40 uppercase mb-1">Gaze</p>
                <p className="text-xs font-bold text-white">{gaze}</p>
              </div>
            </div>

            {alerts.length > 0 && (
              <div className="bg-red-500/10 border border-red-500/20 p-3 rounded-xl">
                <p className="text-[10px] font-bold text-red-400 flex items-center gap-2">
                   <AlertCircle className="w-3 h-3" /> Security Alert Detected
                </p>
              </div>
            )}
          </div>

          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
             <div className="flex items-center gap-2 mb-4">
              <Activity className="text-indigo-400 w-4 h-4" />
              <h3 className="font-bold text-sm uppercase tracking-widest text-white">Metrics</h3>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-[10px] font-bold text-white/40">
                <span>PROGRESS</span>
                <span>{Math.round(progress)}%</span>
              </div>
              <div className="h-1 bg-white/5 rounded-full overflow-hidden">
                <div className="h-full bg-indigo-500 transition-all duration-500" style={{width: `${progress}%`}}></div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default Interview;

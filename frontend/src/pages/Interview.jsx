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
  
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const timerRef = useRef(null);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [alerts, setAlerts] = useState([]);
  const [emotion, setEmotion] = useState("Normal");
  const [gaze, setGaze] = useState("Center");

  useEffect(() => {
    fetchQuestion(true);
    startProctoring();
    return () => {
      stopProctoring();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [id]);

  const startProctoring = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        const interval = setInterval(captureFrame, 3000);
        return () => clearInterval(interval);
      }
    } catch (err) {
      console.warn("Camera access denied");
    }
  };

  const stopProctoring = () => {
    if (videoRef.current?.srcObject) {
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

  const fetchQuestion = async (isFirst = false) => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const url = isFirst 
        ? `http://localhost:8000/interview/${id}/question/0`
        : `http://localhost:8000/interview/${id}/next-question`;
      
      const response = await axios.get(url);
      
      if (response.data.finished) {
        navigate(`/result/${id}`);
        return;
      }
      setQuestionData(response.data);
      setAnswer("");
      setQuestionIndex(prev => isFirst ? 0 : prev + 1);
    } catch (err) {
      setError("Connectivity issue.");
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!answer.trim()) {
      setError("Please provide an answer.");
      return;
    }
    setSubmitting(true);
    try {
      const evalRes = await axios.post(`http://localhost:8000/interview/${id}/submit-response`, null, {
        params: { question_id: questionData.question_id, answer_text: answer }
      });
      
      const star = evalRes.data.star_audit;
      const starStatus = `[S:${star.situation.charAt(0)} T:${star.task.charAt(0)} A:${star.action.charAt(0)} R:${star.result.charAt(0)}]`;
      setSuccess(`Score: ${evalRes.data.score}/10 ${starStatus}`);
      fetchQuestion(false);
    } catch (err) {
      setError("Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const endInterview = () => navigate(`/result/${id}`);
  const progress = questionData ? ((questionIndex + 1) / 10) * 100 : 0;

  if (loading) return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-slate-950 text-white font-['Outfit']">
      <Loader2 className="w-12 h-12 text-indigo-500 animate-spin mb-4" />
      <p className="text-xl font-bold animate-pulse">AI is generating your challenge...</p>
    </div>
  );

  return (
    <div className="max-w-7xl mx-auto px-6 py-12 text-slate-200">
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3 space-y-8">
          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-8 backdrop-blur-xl relative overflow-hidden">
            <div className="mb-6 flex justify-between items-center">
              <div>
                <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">Autonomous Session</span>
                <h2 className="text-sm font-bold text-white/60">Dynamic Flow Active ♾️</h2>
              </div>
              <div className="flex items-center gap-4">
                {success && <div className="text-emerald-400 text-xs font-bold">{success}</div>}
                <div className="text-xs font-medium text-indigo-400 bg-indigo-500/10 px-4 py-2 rounded-xl flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-500 animate-pulse"></div> Adaptive AI
                </div>
              </div>
            </div>

            <motion.h1 
              key={questionData.question_id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-3xl font-bold text-white mb-10 min-h-[100px]"
            >
              {questionData.text}
            </motion.h1>
            
            <div className="space-y-4">
               <div className="flex gap-4 mb-4">
                  <button onClick={() => setInputMode("text")} className={`px-4 py-2 rounded-full text-xs font-bold ${inputMode === "text" ? "bg-indigo-500" : "bg-white/5"}`}>Keyboard</button>
                  <button onClick={() => setInputMode("audio")} className={`px-4 py-2 rounded-full text-xs font-bold ${inputMode === "audio" ? "bg-indigo-500" : "bg-white/5"}`}>Voice AI</button>
               </div>

               {inputMode === "text" ? (
                 <textarea 
                    className="w-full bg-slate-950/50 border border-white/5 rounded-2xl p-6 text-lg min-h-[300px] outline-none"
                    placeholder="Provide your technical insight..."
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                 />
               ) : (
                 <div className="h-[300px] bg-slate-950/50 border border-dashed border-white/10 rounded-2xl flex flex-col items-center justify-center">
                    <button 
                      onClick={isRecording ? stopRecording : startRecording}
                      className={`w-20 h-20 rounded-full flex items-center justify-center ${isRecording ? "bg-red-500" : "bg-indigo-500"}`}
                    >
                      {isRecording ? <Square fill="white" /> : <Mic size={32} />}
                    </button>
                    <p className="mt-6 font-bold text-sm opacity-60 uppercase">{isRecording ? "Listening..." : "Click to Speak"}</p>
                 </div>
               )}
            </div>

            <div className="mt-10 flex justify-between items-center">
              <button onClick={endInterview} className="px-6 py-3 text-red-500 font-bold">End Session</button>
              <button 
                onClick={handleNext} 
                disabled={submitting} 
                className="px-10 py-4 bg-indigo-600 rounded-2xl font-bold text-white shadow-xl shadow-indigo-600/20 disabled:opacity-50"
              >
                {submitting ? <Loader2 className="animate-spin" /> : "Next Challenge"}
              </button>
            </div>
          </div>
        </div>

        <div className="space-y-6">
          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-6 backdrop-blur-xl">
            <h3 className="font-bold text-xs uppercase tracking-widest text-white mb-4">Surveillance</h3>
            <div className="aspect-video bg-black rounded-xl mb-4 overflow-hidden relative">
              <video ref={videoRef} autoPlay playsInline muted className="w-full h-full object-cover grayscale" />
              <canvas ref={canvasRef} className="hidden" />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/5 p-3 rounded-xl">
                <p className="text-[8px] font-bold text-white/40 uppercase">Emotion</p>
                <p className="text-xs font-bold">{emotion}</p>
              </div>
              <div className="bg-white/5 p-3 rounded-xl">
                <p className="text-[8px] font-bold text-white/40 uppercase">Gaze</p>
                <p className="text-xs font-bold">{gaze}</p>
              </div>
            </div>
          </div>
          <div className="bg-slate-900/50 border border-white/10 rounded-3xl p-6">
            <div className="flex justify-between text-[10px] font-bold text-white/40 mb-2">
              <span>PROGRESS</span>
              <span>{Math.round(progress)}%</span>
            </div>
            <div className="h-1 bg-white/5 rounded-full overflow-hidden">
              <div className="h-full bg-indigo-500" style={{width: `${progress}%`}}></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interview;

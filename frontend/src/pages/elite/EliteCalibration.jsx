import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Camera, Mic, Eye, CheckCircle, ArrowRight, Loader2, ShieldCheck } from 'lucide-react';

const EliteCalibration = () => {
  const [steps, setSteps] = useState({
    camera: false,
    audio: false,
    eyeTracking: false,
  });
  const [calibrating, setCalibrating] = useState(false);
  const videoRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    startCamera();
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setSteps(prev => ({ ...prev, camera: true }));
      }
    } catch (err) {
      console.error("Camera access denied");
    }
  };

  const handleCalibration = async () => {
    setCalibrating(true);
    
    // Simulate AI Calibration (inspired by Yoodli/Big Interview guides)
    await new Promise(r => setTimeout(r, 1500));
    setSteps(prev => ({ ...prev, audio: true }));
    
    await new Promise(r => setTimeout(r, 1500));
    setSteps(prev => ({ ...prev, eyeTracking: true }));
    
    setCalibrating(false);
  };

  const proceed = () => {
    navigate('/elite/dashboard');
  };

  return (
    <div className="min-h-screen bg-slate-950 text-white font-['Outfit'] flex flex-col items-center justify-center p-6">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="max-w-4xl w-full bg-slate-900/50 border border-white/10 rounded-[40px] p-12 backdrop-blur-3xl shadow-2xl relative overflow-hidden"
      >
        <div className="absolute top-0 left-0 w-full h-full overflow-hidden -z-10">
          <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-indigo-500/10 rounded-full blur-[120px] animate-pulse"></div>
          <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-purple-500/10 rounded-full blur-[120px] animate-pulse"></div>
        </div>

        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4 bg-gradient-to-r from-white to-white/60 bg-clip-text text-transparent">
            Precision Calibration
          </h1>
          <p className="text-slate-400 max-w-lg mx-auto">
            Ensuring your hardware and environment are optimized for the AI Evaluation Engine.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-3xl blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
            <div className="relative bg-black rounded-3xl overflow-hidden aspect-video border border-white/10">
              <video ref={videoRef} autoPlay muted playsInline className="w-full h-full object-cover scale-x-[-1]" />
              <div className="absolute inset-0 border-[0.5px] border-white/5 pointer-events-none grid grid-cols-3 grid-rows-3">
                {[...Array(9)].map((_, i) => <div key={i} className="border-[0.5px] border-white/5" />)}
              </div>
              {steps.eyeTracking && (
                <motion.div 
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-2 border-indigo-500 rounded-full flex items-center justify-center"
                >
                  <div className="w-2 h-2 bg-indigo-500 rounded-full animate-ping"></div>
                </motion.div>
              )}
            </div>
          </div>

          <div className="flex flex-col justify-center space-y-6">
            <CalibrationItem 
              icon={<Camera size={20} />} 
              label="Visual Identity" 
              desc="Camera feed initialized and clear" 
              status={steps.camera} 
            />
            <CalibrationItem 
              icon={<Mic size={20} />} 
              label="Acoustic Clarity" 
              desc="Microphone levels and background noise check" 
              status={steps.audio} 
            />
            <CalibrationItem 
              icon={<Eye size={20} />} 
              label="Gaze Tracking" 
              desc="Eye-contact calibration with AI focus points" 
              status={steps.eyeTracking} 
            />

            <div className="pt-8">
              {!steps.eyeTracking ? (
                <button 
                  onClick={handleCalibration}
                  disabled={calibrating}
                  className="w-full py-4 bg-white text-slate-950 rounded-2xl font-bold flex items-center justify-center gap-3 hover:bg-slate-200 transition-all shadow-xl shadow-white/5"
                >
                  {calibrating ? <Loader2 className="animate-spin" /> : "Start Auto-Calibration"}
                  {!calibrating && <ShieldCheck size={18} />}
                </button>
              ) : (
                <button 
                  onClick={proceed}
                  className="w-full py-4 bg-indigo-600 text-white rounded-2xl font-bold flex items-center justify-center gap-3 hover:bg-indigo-500 transition-all shadow-xl shadow-indigo-600/20"
                >
                  Enter Elite Dashboard
                  <ArrowRight size={18} />
                </button>
              )}
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
};

const CalibrationItem = ({ icon, label, desc, status }) => (
  <div className={`p-4 rounded-2xl border transition-all ${status ? 'bg-indigo-500/10 border-indigo-500/20' : 'bg-white/5 border-white/5'}`}>
    <div className="flex items-center gap-4">
      <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${status ? 'bg-indigo-500 text-white' : 'bg-white/10 text-slate-400'}`}>
        {icon}
      </div>
      <div className="flex-grow">
        <h3 className="text-sm font-bold">{label}</h3>
        <p className="text-[10px] text-slate-500">{desc}</p>
      </div>
      {status && <CheckCircle size={18} className="text-emerald-500" />}
    </div>
  </div>
);

export default EliteCalibration;

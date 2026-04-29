import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  User, 
  Mail, 
  Briefcase, 
  Code, 
  BarChart, 
  Play, 
  ChevronRight,
  ShieldCheck,
  Settings
} from 'lucide-react';

const Dashboard = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    role: 'Software Engineer',
    skills: [],
    skillInput: '',
    experience: 'Intermediate',
    infiniteMode: false,
    adaptiveAI: true,
    numQuestions: 5
  });

  const handleSkillAdd = (e) => {
    if (e.key === 'Enter' && formData.skillInput.trim()) {
      if (!formData.skills.includes(formData.skillInput.trim())) {
        setFormData({
          ...formData,
          skills: [...formData.skills, formData.skillInput.trim()],
          skillInput: ''
        });
      }
      e.preventDefault();
    }
  };

  const removeSkill = (skillToRemove) => {
    setFormData({
      ...formData,
      skills: formData.skills.filter(s => s !== skillToRemove)
    });
  };

  const startInterview = async () => {
    if (!formData.name || !formData.email) {
      alert("Please fill in basic details.");
      return;
    }
    setLoading(true);
    try {
      const response = await axios.post('http://localhost:8000/interview/start', {
        candidate_name: formData.name,
        candidate_email: formData.email,
        role: formData.role,
        skills: formData.skills,
        experience: formData.experience,
        num_questions: formData.numQuestions,
        infinite_mode: formData.infiniteMode,
        adaptive_mode: formData.adaptiveAI
      });
      navigate(`/interview/${response.data.interview_id}`);
    } catch (error) {
      console.error("Failed to start interview:", error);
      alert("Error starting interview. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8 animate-slide-up">
      <div className="flex justify-between items-center mb-8 bg-gradient-to-r from-blue-600/5 to-purple-600/5 p-6 rounded-3xl border border-white">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Main Dashboard</h2>
          <p className="text-sm text-gray-500">AI-Driven Autonomous System 2.0</p>
        </div>
        <button 
          onClick={() => navigate('/elite/dashboard')}
          className="bg-slate-900 text-white px-6 py-3 rounded-2xl font-bold flex items-center gap-3 hover:bg-slate-800 transition-all shadow-xl shadow-slate-200"
        >
          <span className="flex h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
          Try Elite AI V2
          <ChevronRight size={18} />
        </button>
      </div>
      
      <div className="flex flex-col md:flex-row gap-8">
        
        {/* Left Panel: Configuration */}
        <div className="w-full md:w-1/3 space-y-6">
          <div className="premium-card">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Settings className="text-blue-500 w-5 h-5" />
              Dynamic Setup
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="input-label">Candidate Name</label>
                <div className="relative">
                  <User className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <input 
                    type="text" 
                    className="input-field pl-10" 
                    placeholder="Enter full name"
                    value={formData.name}
                    onChange={(e) => setFormData({...formData, name: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <label className="input-label">Target Role</label>
                <div className="relative">
                  <Briefcase className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <input 
                    type="text" 
                    className="input-field pl-10" 
                    placeholder="e.g. Senior Fullstack Engineer"
                    value={formData.role}
                    onChange={(e) => setFormData({...formData, role: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <label className="input-label">Experience Level</label>
                <input 
                  type="text" 
                  className="input-field" 
                  placeholder="e.g. 5 years, Expert, or Student"
                  value={formData.experience}
                  onChange={(e) => setFormData({...formData, experience: e.target.value})}
                />
              </div>

              <div className="p-4 bg-slate-50 rounded-2xl border border-gray-100 space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-bold text-slate-700">Adaptive AI</p>
                    <p className="text-[10px] text-slate-500">AI adjusts difficulty in real-time</p>
                  </div>
                  <button 
                    onClick={() => setFormData({...formData, adaptiveAI: !formData.adaptiveAI})}
                    className={`w-12 h-6 rounded-full transition-all relative ${formData.adaptiveAI ? 'bg-blue-600' : 'bg-gray-300'}`}
                  >
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${formData.adaptiveAI ? 'left-7' : 'left-1'}`}></div>
                  </button>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-bold text-slate-700">Infinite Mode ♾️</p>
                    <p className="text-[10px] text-slate-500">Session ends only when you stop</p>
                  </div>
                  <button 
                    onClick={() => setFormData({...formData, infiniteMode: !formData.infiniteMode})}
                    className={`w-12 h-6 rounded-full transition-all relative ${formData.infiniteMode ? 'bg-purple-600' : 'bg-gray-300'}`}
                  >
                    <div className={`absolute top-1 w-4 h-4 bg-white rounded-full transition-all ${formData.infiniteMode ? 'left-7' : 'left-1'}`}></div>
                  </button>
                </div>
              </div>

              {!formData.infiniteMode && (
                <div>
                  <label className="input-label">Question Count</label>
                  <input 
                    type="number" 
                    className="input-field" 
                    value={formData.numQuestions}
                    onChange={(e) => setFormData({...formData, numQuestions: parseInt(e.target.value)})}
                  />
                </div>
              )}
            </div>
          </div>

          <div className="premium-card">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Code className="w-4 h-4" /> Skills & Specializations
            </h3>
            <div className="space-y-3">
              <input 
                type="text" 
                className="input-field" 
                placeholder="Type skill and press Enter"
                value={formData.skillInput}
                onChange={(e) => setFormData({...formData, skillInput: e.target.value})}
                onKeyDown={handleSkillAdd}
              />
              <div className="flex flex-wrap gap-2">
                {formData.skills.map(skill => (
                  <span key={skill} className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold border border-blue-100 flex items-center gap-2">
                    {skill}
                    <button onClick={() => removeSkill(skill)} className="hover:text-red-500">×</button>
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Right Panel: Welcome / Preview */}
        <div className="flex-1">
          <div className="bg-white rounded-[32px] p-12 shadow-sm border border-gray-50 h-full flex flex-col justify-center items-center text-center relative overflow-hidden">
             {/* Decorative Elements */}
             <div className="absolute top-0 right-0 w-64 h-64 bg-blue-50 rounded-full -mr-32 -mt-32 opacity-50 blur-3xl"></div>
             <div className="absolute bottom-0 left-0 w-64 h-64 bg-purple-50 rounded-full -ml-32 -mb-32 opacity-50 blur-3xl"></div>

            <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-3xl flex items-center justify-center mb-8 shadow-xl shadow-blue-100 animate-bounce-slow">
              <Play className="text-white fill-current w-10 h-10 ml-1" />
            </div>
            
            <h1 className="text-5xl font-black mb-6 tracking-tight leading-tight">
              RecruitAI <span className="gradient-text">Autonomous</span>
            </h1>
            
            <p className="text-gray-500 max-w-lg mb-12 text-lg leading-relaxed">
              Launch a high-integrity, AI-driven assessment tailored 
              precisely to your role's technical requirements. 
              Zero bias, full transparency.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md mb-12">
               <div className="flex-1 p-5 bg-gray-50/50 backdrop-blur-sm rounded-2xl border border-gray-100 text-left">
                  <div className="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-1">Status</div>
                  <div className="flex items-center gap-2 font-bold text-green-600">
                    <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
                    System Online
                  </div>
               </div>
               <div className="flex-1 p-5 bg-gray-50/50 backdrop-blur-sm rounded-2xl border border-gray-100 text-left">
                  <div className="text-[10px] text-gray-400 uppercase font-bold tracking-widest mb-1">Phase</div>
                  <div className="font-bold text-gray-700">1.0 Core System</div>
               </div>
            </div>

            <button 
              onClick={startInterview}
              disabled={loading}
              className="btn-primary w-full max-w-xs py-5 text-xl rounded-2xl group relative overflow-hidden"
            >
              <span className="relative z-10 flex items-center justify-center gap-2">
                {loading ? "Preparing Session..." : (
                  <>
                    Begin Evaluation
                    <ChevronRight className="w-6 h-6 group-hover:translate-x-1 transition-transform" />
                  </>
                )}
              </span>
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-700 opacity-0 group-hover:opacity-100 transition-opacity"></div>
            </button>
            
            <div className="mt-8 flex items-center gap-6 text-gray-400">
               <div className="flex items-center gap-1.5 text-xs font-medium">
                 <ShieldCheck className="w-4 h-4 text-blue-400" />
                 Secure Storage
               </div>
               <div className="w-1 h-1 bg-gray-200 rounded-full"></div>
               <div className="flex items-center gap-1.5 text-xs font-medium">
                 <BarChart className="w-4 h-4 text-purple-400" />
                 Dynamic Scaling
               </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;

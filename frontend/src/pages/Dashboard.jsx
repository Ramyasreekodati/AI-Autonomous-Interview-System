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
    skills: ['Python'],
    difficulty: 'Medium',
    numQuestions: 5
  });

  const roles = [
    'Software Engineer',
    'Data Scientist',
    'Frontend Developer',
    'ML Engineer',
    'Backend Developer',
    'Full Stack Developer'
  ];

  const skillOptions = [
    'Python', 'React', 'SQL', 'Java', 'Machine Learning', 
    'Deep Learning', 'FastAPI', 'Node.js', 'Docker', 'AWS'
  ];

  const handleSkillToggle = (skill) => {
    if (formData.skills.includes(skill)) {
      setFormData({ ...formData, skills: formData.skills.filter(s => s !== skill) });
    } else {
      setFormData({ ...formData, skills: [...formData.skills, skill] });
    }
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
        difficulty: formData.difficulty,
        num_questions: formData.numQuestions
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
      <div className="flex flex-col md:flex-row gap-8">
        
        {/* Left Panel: Configuration */}
        <div className="w-full md:w-1/3 space-y-6">
          <div className="premium-card">
            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Settings className="text-blue-500 w-5 h-5" />
              Campaign Setup
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
                <label className="input-label">Work Email</label>
                <div className="relative">
                  <Mail className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                  <input 
                    type="email" 
                    className="input-field pl-10" 
                    placeholder="name@company.com"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                  />
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4">
                <div>
                  <label className="input-label">Target Role</label>
                  <div className="relative">
                    <Briefcase className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <select 
                      className="input-field pl-10 appearance-none bg-white"
                      value={formData.role}
                      onChange={(e) => setFormData({...formData, role: e.target.value})}
                    >
                      {roles.map(r => <option key={r} value={r}>{r}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label className="input-label">Difficulty Level</label>
                  <div className="relative">
                    <BarChart className="absolute left-3 top-3 text-gray-400 w-4 h-4" />
                    <select 
                      className="input-field pl-10 appearance-none bg-white"
                      value={formData.difficulty}
                      onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
                    >
                      <option value="Basic">Basic</option>
                      <option value="Medium">Medium</option>
                      <option value="Advanced">Advanced</option>
                    </select>
                  </div>
                </div>
              </div>

              <div>
                <div className="flex justify-between items-center mb-1">
                  <label className="input-label mb-0">Questions Count</label>
                  <span className="text-blue-600 font-bold text-sm bg-blue-50 px-2 py-0.5 rounded-full">{formData.numQuestions}</span>
                </div>
                <input 
                  type="range" 
                  min="1" max="20" 
                  className="w-full h-1.5 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
                  value={formData.numQuestions}
                  onChange={(e) => setFormData({...formData, numQuestions: parseInt(e.target.value)})}
                />
              </div>
            </div>
          </div>

          <div className="premium-card">
            <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-4 flex items-center gap-2">
              <Code className="w-4 h-4" /> Specializations
            </h3>
            <div className="flex flex-wrap gap-2">
              {skillOptions.map(skill => (
                <button
                  key={skill}
                  onClick={() => handleSkillToggle(skill)}
                  className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all duration-200 ${
                    formData.skills.includes(skill)
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-200 ring-2 ring-blue-100'
                      : 'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-100'
                  }`}
                >
                  {skill}
                </button>
              ))}
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

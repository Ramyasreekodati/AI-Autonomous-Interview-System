import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  TrendingUp, 
  CheckCircle, 
  Activity, 
  Award, 
  PlayCircle, 
  Video, 
  ArrowRight,
  Brain,
  LayoutDashboard,
  FileText,
  BookOpen,
  Search,
  Filter,
  Settings,
  ShieldCheck,
  Zap
} from 'lucide-react';

const EliteDashboard = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState("");

  const questionCategories = [
    { title: "Software Engineering", count: 450, icon: "💻" },
    { title: "Product Management", count: 280, icon: "📦" },
    { title: "Data Science", count: 320, icon: "📊" },
    { title: "Design / UX", count: 190, icon: "🎨" }
  ];

  return (
    <div className="flex min-h-screen bg-[#0F172A] text-slate-100 font-['Outfit']">
      {/* Sidebar */}
      <aside className="w-[280px] bg-[#1E293B] p-8 flex flex-col border-r border-white/10 fixed h-full z-50">
        <div className="flex items-center gap-3 text-2xl font-bold mb-16 bg-gradient-to-r from-white to-[#10B981] bg-clip-text text-transparent cursor-pointer" onClick={() => navigate('/')}>
          <Brain className="text-[#10B981] w-8 h-8" />
          <span>InterviewAI</span>
        </div>
        
        <nav className="flex-grow">
          <ul className="space-y-2">
            <NavItem icon={<LayoutDashboard size={20} />} label="Home" active />
            <NavItem icon={<Activity size={20} />} label="Dashboard" />
            <NavItem icon={<Video size={20} />} label="Practice Room" onClick={() => navigate('/elite/calibration')} />
            <NavItem icon={<BookOpen size={20} />} label="Question Bank" />
            <NavItem icon={<FileText size={20} />} label="Resume AI" />
          </ul>
        </nav>

        <div className="mt-auto space-y-4">
          <div 
            onClick={() => navigate('/elite/calibration')}
            className="bg-indigo-500/10 border border-indigo-500/20 rounded-2xl p-4 cursor-pointer hover:bg-indigo-500/20 transition-all group"
          >
            <div className="flex items-center justify-between mb-2">
              <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-widest">System Readiness</p>
              <ShieldCheck size={14} className="text-indigo-400" />
            </div>
            <div className="flex items-center gap-2">
               <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
               <span className="text-xs font-bold group-hover:translate-x-1 transition-transform">Ready for Mock</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-[280px] flex-grow p-12 max-w-[1400px]">
        <motion.header 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12 flex justify-between items-end"
        >
          <div>
            <h1 className="text-4xl font-bold mb-2">Elite Command Center</h1>
            <p className="text-slate-400">Autonomous Interview Intelligence System v2.1</p>
          </div>
          <button 
            onClick={() => navigate('/elite/calibration')}
            className="bg-white text-slate-950 px-8 py-4 rounded-2xl font-bold flex items-center gap-3 hover:bg-slate-200 transition-all shadow-xl shadow-white/5"
          >
            <Zap size={18} className="fill-slate-950" />
            Start AI Mock Interview
          </button>
        </motion.header>

        {/* Search Question Library (Big Interview Feature) */}
        <div className="mb-12 relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#10B981] to-[#3B82F6] rounded-3xl blur opacity-10 group-hover:opacity-25 transition duration-1000"></div>
          <div className="relative bg-[#1E293B] border border-white/5 rounded-3xl p-2 flex items-center">
            <Search className="ml-4 text-slate-500" />
            <input 
              type="text" 
              placeholder="Search 5,000+ technical and behavioral questions..."
              className="bg-transparent border-none outline-none flex-grow p-4 text-lg placeholder:text-slate-600"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            <button className="bg-white/5 text-slate-400 px-6 py-3 rounded-2xl flex items-center gap-2 hover:bg-white/10 transition-all mr-2 font-semibold">
              <Filter size={18} /> Filters
            </button>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard label="Technical Depth" value="Elite" icon={<Brain className="text-[#10B981]" />} />
          <StatCard label="Avg. Score" value="8.4/10" icon={<Award className="text-[#F59E0B]" />} />
          <StatCard label="Gaze Consistency" value="92%" icon={<Activity className="text-[#3B82F6]" />} />
          <StatCard label="Integrity Level" value="Safe" icon={<ShieldCheck className="text-[#10B981]" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Question Categories */}
          <div className="lg:col-span-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8">
            <div className="flex justify-between items-center mb-8">
              <h3 className="text-xl font-bold">Curated Libraries</h3>
              <button className="text-[#10B981] text-sm font-bold hover:underline">View All</button>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {questionCategories.map(cat => (
                <div key={cat.title} className="p-6 bg-white/5 rounded-2xl border border-white/5 hover:border-[#10B981]/30 hover:bg-white/10 transition-all cursor-pointer group">
                  <div className="text-3xl mb-4 group-hover:scale-110 transition-transform">{cat.icon}</div>
                  <h4 className="font-bold text-lg mb-1">{cat.title}</h4>
                  <p className="text-xs text-slate-500">{cat.count} Professional Questions</p>
                </div>
              ))}
            </div>
          </div>

          {/* Activity Feed */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 flex flex-col">
            <h3 className="text-xl font-bold mb-2">Resume Intelligence</h3>
            <p className="text-slate-400 text-sm mb-8">ATS Analysis & Feedback</p>
            
            <div className="space-y-4 mb-8">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                <span className="text-sm">Readability</span>
                <span className="font-bold text-emerald-400">92%</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                <span className="text-sm">Credibility</span>
                <span className="font-bold text-blue-400">84%</span>
              </div>
            </div>

            <div className="mt-auto">
              <button className="w-full bg-white/5 border border-white/10 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-2 hover:bg-white/10 transition-all">
                Upload New Resume <FileText size={18} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ icon, label, active = false, onClick }) => (
  <li>
    <div 
      onClick={onClick}
      className={`flex items-center gap-3 p-3 rounded-xl transition-all cursor-pointer ${active ? 'bg-white/5 text-white border-l-4 border-[#10B981]' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}
    >
      {icon}
      <span className="font-semibold">{label}</span>
    </div>
  </li>
);

const StatCard = ({ label, value, icon }) => (
  <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 flex flex-col items-center justify-center group hover:bg-white/10 transition-all">
    <div className="w-12 h-12 rounded-2xl bg-white/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <div className="text-2xl font-bold mb-1">{value}</div>
    <p className="text-slate-500 text-[10px] font-bold uppercase tracking-widest">{label}</p>
  </div>
);

export default EliteDashboard;

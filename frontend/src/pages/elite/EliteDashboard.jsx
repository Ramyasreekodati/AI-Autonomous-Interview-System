import React from 'react';
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
  BookOpen
} from 'lucide-react';

const EliteDashboard = () => {
  return (
    <div className="flex min-h-screen bg-[#0F172A] text-slate-100 font-['Outfit']">
      {/* Sidebar - Ported from Elite Design */}
      <aside className="w-[280px] bg-[#1E293B] p-8 flex flex-col border-r border-white/10 fixed h-full z-50">
        <div className="flex items-center gap-3 text-2xl font-bold mb-16 bg-gradient-to-r from-white to-[#10B981] bg-clip-text text-transparent">
          <Brain className="text-[#10B981] w-8 h-8" />
          <span>InterviewAI</span>
        </div>
        
        <nav className="flex-grow">
          <ul className="space-y-2">
            <NavItem icon={<LayoutDashboard size={20} />} label="Home" active />
            <NavItem icon={<Activity size={20} />} label="Dashboard" />
            <NavItem icon={<Video size={20} />} label="Practice Room" />
            <NavItem icon={<BookOpen size={20} />} label="Curriculum" />
            <NavItem icon={<FileText size={20} />} label="Resume AI" />
          </ul>
        </nav>

        <div className="mt-auto">
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-4">
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-2">Pro Plan Active</p>
            <div className="h-1 bg-white/10 rounded-full overflow-hidden">
              <div className="w-3/4 h-full bg-[#10B981]"></div>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="ml-[280px] flex-grow p-12 max-w-[1400px]">
        <motion.header 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold mb-2">Welcome Back, Candidate</h1>
          <p className="text-slate-400">Consistency is the key to success. You've practiced 4 days this week!</p>
        </motion.header>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <StatCard label="Weekly Goal" value="75%" type="circle" />
          <StatCard label="Sessions" value="12" icon={<TrendingUp className="text-[#10B981]" />} />
          <StatCard label="Confidence" value="84%" icon={<Activity className="text-[#3B82F6]" />} />
          <StatCard label="Current Grade" value="A-" icon={<Award className="text-[#8B5CF6]" />} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Recent Activity */}
          <div className="lg:col-span-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8">
            <h3 className="text-xl font-bold mb-6">Recent Activity</h3>
            <div className="space-y-4">
              <ActivityItem 
                icon={<PlayCircle className="text-[#10B981]" />} 
                title="Behavioral Interviewing 101" 
                time="Completed 15 mins ago" 
              />
              <ActivityItem 
                icon={<Video className="text-[#3B82F6]" />} 
                title="Mock Interview: Senior SWE" 
                time="Completed yesterday" 
              />
            </div>
          </div>

          {/* Next Up */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 flex flex-col">
            <h3 className="text-xl font-bold mb-2">Next Up</h3>
            <p className="text-slate-400 text-sm mb-8">Recommended for your progress</p>
            
            <div className="mt-auto">
              <button className="w-full bg-gradient-to-r from-[#3B82F6] to-[#10B981] text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-2 hover:shadow-lg hover:shadow-blue-500/20 transition-all">
                Mastering Body Language <ArrowRight size={18} />
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const NavItem = ({ icon, label, active = false }) => (
  <li>
    <a href="#" className={`flex items-center gap-3 p-3 rounded-xl transition-all ${active ? 'bg-white/5 text-white border-l-4 border-[#10B981]' : 'text-slate-400 hover:bg-white/5 hover:text-white'}`}>
      {icon}
      <span className="font-semibold">{label}</span>
    </a>
  </li>
);

const StatCard = ({ label, value, icon, type = "default" }) => (
  <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-3xl p-8 flex flex-col items-center justify-center">
    {type === "circle" ? (
      <div className="relative w-24 h-24 mb-4">
        <svg className="w-full h-full transform -rotate-90">
          <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-white/10" />
          <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray="251.2" strokeDashoffset={251.2 * 0.25} className="text-[#10B981]" />
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-bold text-xl">{value}</span>
      </div>
    ) : (
      <div className="text-3xl font-bold mb-2 flex items-center gap-3">
        {value}
      </div>
    )}
    <p className="text-slate-400 text-sm font-semibold uppercase tracking-widest">{label}</p>
  </div>
);

const ActivityItem = ({ icon, title, time }) => (
  <div className="flex items-center gap-4 p-4 rounded-2xl hover:bg-white/5 transition-all cursor-pointer group">
    <div className="w-12 h-12 rounded-xl bg-white/5 flex items-center justify-center group-hover:scale-110 transition-transform">
      {icon}
    </div>
    <div>
      <h4 className="font-bold">{title}</h4>
      <p className="text-xs text-slate-400">{time}</p>
    </div>
  </div>
);

export default EliteDashboard;

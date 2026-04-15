import React from 'react';
import { motion } from 'framer-motion';
import { Trophy, FileText, CheckCircle, BarChart, Download } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import axios from 'axios';

const Dashboard = () => {
    const navigate = useNavigate();
    const { id: interviewId } = useParams();
    const [results, setResults] = React.useState(null);

    React.useEffect(() => {
        fetchResults();
    }, []);

    const fetchResults = async () => {
        try {
            const response = await axios.get(`http://localhost:8000/interview/${interviewId}/results`);
            setResults(response.data);
        } catch (err) {
            console.error(err);
        }
    };
    
    if (!results) return <div className="p-20 text-center">Loading Analytics...</div>;

    return (
        <div className="min-h-screen bg-slate-50 p-8">
            <div className="max-w-6xl mx-auto">
                <header className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 mb-12">
                    <div>
                        <div className="flex items-center gap-2 mb-2">
                          <CheckCircle className="text-indigo-600 w-5 h-5" />
                          <span className="text-xs font-bold text-indigo-600 uppercase tracking-widest">Feedback Analysis</span>
                        </div>
                        <h1 className="text-4xl font-extrabold text-slate-900 tracking-tight">Executive Report</h1>
                        <p className="text-slate-500 font-medium mt-1">Interview session ID: {interviewId}</p>
                    </div>
                    <button className="btn-primary py-3 px-6 shadow-xl">
                        <Download className="w-5 h-5" /> Export PDF Report
                    </button>
                </header>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-10">
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95 }} 
                      animate={{ opacity: 1, scale: 1 }} 
                      className="premium-card flex flex-col items-center justify-center py-10"
                    >
                         <div className="relative mb-6">
                            <svg className="w-24 h-24 transform -rotate-90">
                              <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-100" />
                              <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray="251.2" strokeDashoffset={251.2 * (1 - results.interview_score / 100)} className="text-indigo-600" />
                            </svg>
                            <span className="absolute inset-0 flex items-center justify-center text-3xl font-black text-slate-900">{results.interview_score}</span>
                         </div>
                         <p className="text-slate-400 font-bold text-[10px] uppercase tracking-widest">Interview Score</p>
                    </motion.div>
                    
                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95 }} 
                      animate={{ opacity: 1, scale: 1 }} 
                      transition={{ delay: 0.1 }} 
                      className="premium-card flex flex-col items-center justify-center py-10"
                    >
                         <div className="relative mb-6">
                            <svg className="w-24 h-24 transform -rotate-90">
                              <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" className="text-slate-100" />
                              <circle cx="48" cy="48" r="40" stroke="currentColor" strokeWidth="8" fill="transparent" strokeDasharray="251.2" strokeDashoffset={251.2 * (1 - results.behavior_score / 100)} className="text-emerald-500" />
                            </svg>
                            <span className="absolute inset-0 flex items-center justify-center text-3xl font-black text-slate-900">{results.behavior_score}</span>
                         </div>
                         <p className="text-slate-400 font-bold text-[10px] uppercase tracking-widest">Behavior Integrity</p>
                    </motion.div>

                    <motion.div 
                      initial={{ opacity: 0, scale: 0.95 }} 
                      animate={{ opacity: 1, scale: 1 }} 
                      transition={{ delay: 0.2 }} 
                      className={`premium-card flex flex-col items-center justify-center py-10 border-l-4 ${results.risk_level === 'High' ? 'border-l-rose-500' : 'border-l-emerald-500'}`}
                    >
                         <div className="w-20 h-20 rounded-2xl bg-slate-50 flex items-center justify-center mb-6">
                             {results.risk_level === 'High' ? <AlertCircle className="text-rose-500 w-10 h-10" /> : <CheckCircle className="text-emerald-500 w-10 h-10" />}
                         </div>
                         <p className="text-slate-400 font-bold text-[10px] uppercase tracking-widest mb-1">Risk Assessment</p>
                         <p className={`text-sm font-black uppercase ${results.risk_level === 'High' ? 'text-rose-500' : 'text-emerald-500'}`}>{results.risk_level} Risk</p>
                    </motion.div>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <section className="premium-card">
                        <h3 className="text-lg font-extrabold text-slate-900 mb-8 flex items-center gap-3">
                            <Trophy className="text-indigo-600 w-5 h-5" /> Qualitative Insights
                        </h3>
                        <div className="space-y-4">
                            {[
                                { name: "Technical Precision", value: "High", color: "badge-low" },
                                { name: "Engagement Level", value: "Excellent", color: "badge-low" },
                                { name: "Response Consistency", value: "Developing", color: "badge-medium" }
                            ].map((item, idx) => (
                                <div key={idx} className="flex items-center justify-between p-4 bg-slate-50/50 border border-slate-100 rounded-xl">
                                    <span className="text-sm font-semibold text-slate-700">{item.name}</span>
                                    <span className={`badge ${item.color}`}>{item.value}</span>
                                </div>
                            ))}
                        </div>
                    </section>

                    <section className="premium-card">
                        <h3 className="text-lg font-extrabold text-slate-900 mb-8 flex items-center gap-3">
                            <BarChart className="text-indigo-600 w-5 h-5" /> Competency Breakdown
                        </h3>
                        <div className="space-y-8">
                            {[
                                { name: "Problem Solving", score: 85 },
                                { name: "System Design", score: 60 }
                            ].map((item, idx) => (
                                <div key={idx}>
                                    <div className="flex justify-between text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">
                                        <span>{item.name}</span>
                                        <span className="text-slate-900">{item.score}%</span>
                                    </div>
                                    <div className="w-full bg-slate-100 h-2.5 rounded-full overflow-hidden">
                                        <motion.div 
                                          initial={{ width: 0 }}
                                          animate={{ width: `${item.score}%` }}
                                          transition={{ duration: 1, delay: 0.5 }}
                                          className="bg-indigo-600 h-full rounded-full" 
                                        />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
                
                <div className="mt-16 text-center">
                     <button onClick={() => navigate('/')} className="text-sm font-bold text-slate-400 hover:text-indigo-600 transition-all uppercase tracking-widest">
                        Return to Dashboard
                     </button>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;

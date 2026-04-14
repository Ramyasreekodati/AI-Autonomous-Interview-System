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
        <div className="min-h-screen p-8 max-w-6xl mx-auto">
            <header className="flex justify-between items-center mb-12">
                <div>
                    <h1 className="text-4xl font-bold gradient-text mb-2">Interview Analysis</h1>
                    <p className="text-text-muted">Comprehensive evaluation feedback</p>
                </div>
                <button className="btn-primary flex items-center gap-2">
                    <Download className="w-5 h-5" /> Download PDF Report
                </button>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="glass-card flex flex-col items-center justify-center p-12">
                     <div className="w-24 h-24 rounded-full border-4 border-primary/30 flex items-center justify-center mb-4">
                        <span className="text-4xl font-bold">{results.interview_score}</span>
                     </div>
                     <p className="text-text-muted uppercase text-xs tracking-widest">Interview Score</p>
                </motion.div>
                
                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card flex flex-col items-center justify-center p-12">
                     <div className="w-24 h-24 rounded-full border-4 border-accent/30 flex items-center justify-center mb-4 text-accent">
                        <span className="text-4xl font-bold">{results.behavior_score}</span>
                     </div>
                     <p className="text-text-muted uppercase text-xs tracking-widest">Behavior Score</p>
                </motion.div>

                <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} className="glass-card flex flex-col items-center justify-center p-12">
                     <div className={`w-24 h-24 rounded-full border-4 ${results.risk_level === 'High' ? 'border-error/30 text-error' : 'border-accent/30 text-accent'} flex items-center justify-center mb-4`}>
                        <span className="text-4xl font-bold">{results.alert_count}</span>
                     </div>
                     <p className="text-text-muted uppercase text-xs tracking-widest">Risk Alerts ({results.risk_level})</p>
                </motion.div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <section className="glass-card">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <CheckCircle className="text-accent" /> Strong Attributes
                    </h3>
                    <ul className="space-y-4">
                        <li className="bg-surface-light p-4 rounded-xl flex justify-between border-l-4 border-accent">
                            <span>Technical Communication</span>
                            <span className="text-accent font-bold">High</span>
                        </li>
                        <li className="bg-surface-light p-4 rounded-xl flex justify-between border-l-4 border-accent">
                            <span>Confidence Level</span>
                            <span className="text-accent font-bold">Excellent</span>
                        </li>
                        <li className="bg-surface-light p-4 rounded-xl flex justify-between border-l-4 border-orange-500">
                            <span>Problem Solving</span>
                            <span className="text-orange-500 font-bold">Average</span>
                        </li>
                    </ul>
                </section>

                <section className="glass-card">
                    <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                        <BarChart className="text-primary" /> Topic Coverage
                    </h3>
                    <div className="space-y-6">
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span>Core Programming</span>
                                <span>90%</span>
                            </div>
                            <div className="w-full bg-surface-light h-2 rounded-full">
                                <div className="bg-primary h-full w-[90%] rounded-full shadow-[0_0_10px_var(--primary)]" />
                            </div>
                        </div>
                        <div>
                            <div className="flex justify-between text-sm mb-2">
                                <span>System Design</span>
                                <span>65%</span>
                            </div>
                            <div className="w-full bg-surface-light h-2 rounded-full">
                                <div className="bg-primary h-full w-[65%] rounded-full opacity-70" />
                            </div>
                        </div>
                    </div>
                </section>
            </div>
            
            <div className="mt-12 text-center">
                 <button onClick={() => navigate('/')} className="text-text-muted hover:text-white transition-colors">
                    Back to Portal Home
                 </button>
            </div>
        </div>
    );
};

export default Dashboard;

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Download, 
  Home, 
  CheckCircle2, 
  AlertTriangle, 
  BarChart3, 
  ShieldCheck,
  ChevronRight,
  TrendingUp,
  Loader2
} from 'lucide-react';

const Result = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchResults();
  }, [id]);

  const fetchResults = async () => {
    try {
      const response = await axios.get(`http://localhost:8000/interview/${id}/report`);
      // Since the endpoint returns a file in the user's backend, we might need a separate endpoint for JSON results
      // Let's call the results endpoint
      const resData = await axios.get(`http://localhost:8000/interview/${id}/results`);
      setResults(resData.data);
    } catch (err) {
      console.error("Failed to fetch results", err);
    } finally {
      setLoading(false);
    }
  };

  const downloadReport = () => {
    window.open(`http://localhost:8000/interview/${id}/report`, '_blank');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="w-10 h-10 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-500 font-medium tracking-tight">Synthesizing Final Report...</p>
      </div>
    );
  }

  const isPass = results?.final_decision === "pass";

  return (
    <div className="max-w-4xl mx-auto px-4 py-16 animate-slide-up">
      <div className="text-center mb-12">
        <div className={`w-20 h-20 rounded-3xl mx-auto flex items-center justify-center mb-6 shadow-xl ${
          isPass ? 'bg-green-100 text-green-600' : 'bg-red-100 text-red-600'
        }`}>
          {isPass ? <CheckCircle2 className="w-10 h-10" /> : <AlertTriangle className="w-10 h-10" />}
        </div>
        <h1 className="text-4xl font-black text-gray-900 mb-2">Interview Concluded</h1>
        <p className="text-gray-500 font-medium">Data-driven assessment has been generated.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <ScoreCard 
          label="Technical Quality" 
          value={`${results?.interview_score}/10`} 
          sub="Accuracy & Depth" 
          icon={<BarChart3 className="text-blue-500" />}
        />
        <ScoreCard 
          label="Integrity Score" 
          value={`${results?.behavior_score}%`} 
          sub="Proctoring Loyalty" 
          icon={<ShieldCheck className="text-purple-500" />}
        />
        <ScoreCard 
          label="Risk Assessment" 
          value={results?.risk_level.toUpperCase()} 
          sub="Session Safety" 
          icon={<TrendingUp className={results?.risk_level === 'low' ? 'text-green-500' : 'text-red-500'} />}
        />
      </div>

      <div className="premium-card mb-8">
        <h3 className="text-lg font-bold mb-4 flex items-center gap-2">
          Assessment Justification
        </h3>
        <p className="text-gray-600 leading-relaxed bg-gray-50 p-6 rounded-2xl border border-gray-100 italic">
          "{results?.justification}"
        </p>
        
        {results?.alerts.length > 0 && (
          <div className="mt-8">
            <h4 className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4">Logged Violations</h4>
            <div className="flex flex-wrap gap-2">
              {results?.alerts.map(alert => (
                <span key={alert} className="px-3 py-1 bg-red-50 text-red-600 text-[10px] font-bold rounded-full border border-red-100 uppercase">
                  {alert.replace('_', ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>

      <div className="flex flex-col sm:flex-row gap-4">
        <button 
          onClick={downloadReport}
          className="btn-primary flex-1 py-4 text-lg rounded-2xl"
        >
          <Download className="w-5 h-5" /> Download PDF Report
        </button>
        <button 
          onClick={() => navigate('/dashboard')}
          className="btn-secondary py-4 px-8 rounded-2xl flex items-center gap-2"
        >
          <Home className="w-5 h-5" /> Back to Setup
        </button>
      </div>
    </div>
  );
};

const ScoreCard = ({ label, value, sub, icon }) => (
  <div className="premium-card !p-6 flex flex-col items-center text-center">
    <div className="mb-4">{icon}</div>
    <div className="text-sm font-bold text-gray-400 uppercase tracking-widest mb-1">{label}</div>
    <div className="text-3xl font-black text-gray-900 mb-1">{value}</div>
    <div className="text-xs text-gray-400">{sub}</div>
  </div>
);

export default Result;

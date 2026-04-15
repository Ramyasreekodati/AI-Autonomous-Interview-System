import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { User, Mail, ArrowRight } from 'lucide-react';
import axios from 'axios';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isRegistering, setIsRegistering] = useState(false);
  const [name, setName] = useState('');
  const navigate = useNavigate();

  const handleStart = async (e) => {
    e.preventDefault();
    try {
      if (isRegistering) {
        await axios.post('http://127.0.0.1:8000/auth/register', { name, email, password });
        setIsRegistering(false);
        // Using a cleaner alert would be better but keeping it simple for now
        alert("Registration successful! Please login.");
        return;
      }

      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('http://127.0.0.1:8000/auth/login', formData);
      localStorage.setItem('token', response.data.access_token);
      
      const sessRes = await axios.post('http://127.0.0.1:8000/interview/start', null, {
        params: { candidate_email: email }
      });
      navigate(`/interview/${sessRes.data.interview_id}`);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.detail || "Authentication failed.");
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen p-6 bg-slate-50">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.4 }}
        className="premium-card w-full max-w-md"
      >
        <div className="text-center mb-10">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-600 mb-6 shadow-indigo-200 shadow-xl">
            <User className="text-white w-8 h-8" />
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 mb-2">RecruitAI</h1>
          <p className="text-slate-500 font-medium">Autonomous Interview Intelligence</p>
        </div>

        <form onSubmit={handleStart} className="space-y-6">
          {isRegistering && (
            <div className="space-y-2">
              <label className="input-label">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
                <input 
                  type="text" 
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="input-field pl-11"
                  placeholder="John Doe"
                />
              </div>
            </div>
          )}
          
          <div className="space-y-2">
            <label className="input-label">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-field pl-11"
                placeholder="candidate@example.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="input-label">Password</label>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 w-5 h-5 flex items-center justify-center font-bold">*</div>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input-field pl-11"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button type="submit" className="btn-primary w-full py-3.5 mt-2">
            {isRegistering ? "Create Account" : "Begin Evaluation"}
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <div className="mt-6 text-center">
            <button 
                onClick={() => setIsRegistering(!isRegistering)}
                className="text-sm font-semibold text-indigo-600 hover:text-indigo-700 transition-colors"
            >
                {isRegistering ? "Already have an account? Sign in" : "New candidate? Create account"}
            </button>
        </div>

        <div className="mt-10 pt-6 border-t border-slate-100 flex items-center justify-center gap-2 text-xs font-semibold uppercase tracking-wider text-slate-400">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
          AI Monitoring Active
        </div>
      </motion.div>
    </div>
  );
};

export default Login;

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
        alert("Registration successful! Please login.");
        return;
      }

      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post('http://127.0.0.1:8000/auth/login', formData);
      localStorage.setItem('token', response.data.access_token);
      
      // Start session
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
    <div className="flex items-center justify-center min-h-screen p-4">
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="glass-card w-full max-w-md"
      >
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold mb-2 gradient-text">RecruitAI</h1>
          <p className="text-text-muted">Autonomous Interview Intelligence</p>
        </div>

        <form onSubmit={handleStart} className="space-y-6">
          {isRegistering && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-text-muted">Full Name</label>
              <div className="relative">
                <User className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted w-5 h-5" />
                <input 
                  type="text" 
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full bg-surface-light border border-border rounded-lg py-3 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                  placeholder="John Doe"
                />
              </div>
            </div>
          )}
          
          <div className="space-y-2">
            <label className="text-sm font-medium text-text-muted">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted w-5 h-5" />
              <input 
                type="email" 
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-surface-light border border-border rounded-lg py-3 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                placeholder="candidate@example.com"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-text-muted">Password</label>
            <div className="relative">
              <div className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted w-5 h-5 flex items-center justify-center font-bold">*</div>
              <input 
                type="password" 
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-surface-light border border-border rounded-lg py-3 pl-12 pr-4 focus:ring-2 focus:ring-primary focus:outline-none transition-all"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button type="submit" className="btn-primary w-full flex items-center justify-center gap-2 group">
            {isRegistering ? "Create Account" : "Begin Evaluation"}
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </form>

        <div className="mt-4 text-center">
            <button 
                onClick={() => setIsRegistering(!isRegistering)}
                className="text-sm text-primary hover:underline"
            >
                {isRegistering ? "Already have an account? Login" : "New candidate? Register here"}
            </button>
        </div>

        <div className="mt-8 pt-6 border-t border-border text-center text-xs text-text-muted">
          AI Monitoring will be active during this session
        </div>
      </motion.div>
    </div>
  );
};

export default Login;

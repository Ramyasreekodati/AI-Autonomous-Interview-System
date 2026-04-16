import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { 
  Mic, 
  Type, 
  ChevronLeft, 
  ChevronRight, 
  Send,
  Loader2,
  AlertCircle,
  Clock,
  CheckCircle2
} from 'lucide-react';

const Interview = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [questionIndex, setQuestionIndex] = useState(0);
  const [questionData, setQuestionData] = useState(null);
  const [answer, setAnswer] = useState("");
  const [inputMode, setInputMode] = useState("text"); // 'text' or 'audio'
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  useEffect(() => {
    fetchQuestion(0);
  }, [id]);

  const fetchQuestion = async (index) => {
    setLoading(true);
    setError("");
    setSuccess("");
    try {
      const response = await axios.get(`http://localhost:8000/interview/${id}/question/${index}`);
      if (response.data.finished) {
        navigate(`/result/${id}`);
        return;
      }
      setQuestionData(response.data);
      setAnswer(response.data.previous_answer || "");
      setQuestionIndex(index);
    } catch (err) {
      setError("Failed to load question. Make sure backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleNext = async () => {
    if (!answer.trim()) {
      setError("Please provide an answer before moving to the next question.");
      return;
    }
    
    setSubmitting(true);
    setError("");
    try {
      const response = await axios.post(`http://localhost:8000/interview/${id}/submit-response`, null, {
        params: {
          question_id: questionData.question_id,
          answer_text: answer
        }
      });
      
      if (response.data.status === "invalid") {
        setError("Invalid input detected. Please provide a meaningful answer.");
        setSubmitting(false);
        return;
      }

      setSuccess("Answer saved!");
      setTimeout(() => {
        fetchQuestion(questionIndex + 1);
      }, 500);
    } catch (err) {
      setError(err.response?.data?.detail || "Submission failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePrevious = () => {
    if (questionIndex > 0) {
      fetchQuestion(questionIndex - 1);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-gray-50">
        <Loader2 className="w-12 h-12 text-blue-600 animate-spin mb-4" />
        <p className="text-gray-500 font-medium">Loading session data...</p>
      </div>
    );
  }

  const progress = questionData ? ((questionIndex + 1) / questionData.total) * 100 : 0;

  return (
    <div className="max-w-5xl mx-auto px-4 py-12 animate-slide-up">
      {/* Header & Progress */}
      <div className="mb-12">
        <div className="flex justify-between items-center mb-4">
          <div>
            <span className="bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider">
              Question {questionIndex + 1} of {questionData?.total}
            </span>
          </div>
          <div className="flex items-center gap-2 text-gray-400 text-sm font-medium">
            <Clock className="w-4 h-4" />
            Live Session
          </div>
        </div>
        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div 
            className="h-full bg-blue-600 transition-all duration-500 ease-out"
            style={{ width: `${progress}%` }}
          ></div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Panel: Question & Input */}
        <div className="lg:col-span-2 space-y-6">
          <div className="premium-card min-h-[500px] flex flex-col">
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900 mb-8 leading-tight">
                {questionData?.text}
              </h1>

              {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-100 text-red-600 rounded-2xl flex items-center gap-3 text-sm animate-shake">
                  <AlertCircle className="w-5 h-5 flex-shrink-0" />
                  {error}
                </div>
              )}

              {success && (
                <div className="mb-6 p-4 bg-green-50 border border-green-100 text-green-600 rounded-2xl flex items-center gap-3 text-sm">
                  <CheckCircle2 className="w-5 h-5 flex-shrink-0" />
                  {success}
                </div>
              )}

              <div className="space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <label className="input-label mb-0">Your Response</label>
                  <div className="flex bg-gray-100 p-1 rounded-xl">
                    <button 
                      onClick={() => setInputMode("text")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                        inputMode === "text" ? "bg-white text-blue-600 shadow-sm" : "text-gray-500"
                      }`}
                    >
                      <Type className="w-3.5 h-3.5" /> Keyboard
                    </button>
                    <button 
                      onClick={() => setInputMode("audio")}
                      className={`px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5 transition-all ${
                        inputMode === "audio" ? "bg-white text-blue-600 shadow-sm" : "text-gray-500"
                      }`}
                    >
                      <Mic className="w-3.5 h-3.5" /> Voice
                    </button>
                  </div>
                </div>

                {inputMode === "text" ? (
                  <textarea
                    className="input-field min-h-[250px] resize-none p-6 text-lg"
                    placeholder="Type your detailed answer here..."
                    value={answer}
                    onChange={(e) => setAnswer(e.target.value)}
                  ></textarea>
                ) : (
                  <div className="min-h-[250px] flex flex-col items-center justify-center border-2 border-dashed border-gray-200 rounded-3xl bg-gray-50/50 p-10">
                    <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6 cursor-pointer hover:bg-blue-200 transition-colors group">
                      <Mic className="text-blue-600 w-8 h-8 group-active:scale-90 transition-transform" />
                    </div>
                    <p className="text-gray-500 font-medium">Click to Start Recording</p>
                    <p className="text-xs text-gray-400 mt-2">Phase 1: Recording UI Only</p>
                  </div>
                )}
              </div>
            </div>

            {/* Navigation */}
            <div className="mt-12 flex justify-between items-center bg-gray-50 -mx-10 -mb-10 p-6 px-10 rounded-b-[20px] border-t border-gray-100">
              <button 
                onClick={handlePrevious}
                disabled={questionIndex === 0 || submitting}
                className="btn-secondary flex items-center gap-2 disabled:opacity-30"
              >
                <ChevronLeft className="w-5 h-5" /> Previous
              </button>
              
              <button 
                onClick={handleNext}
                disabled={submitting}
                className="btn-primary min-w-[140px]"
              >
                {submitting ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <>
                    {questionIndex + 1 === questionData?.total ? "Finish" : "Next Question"}
                    <ChevronRight className="w-5 h-5" />
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Side Panel: Info */}
        <div className="space-y-6">
          <div className="premium-card">
            <h3 className="font-bold text-gray-900 mb-4">Interview Guidelines</h3>
            <ul className="space-y-4">
              <li className="flex gap-3 text-sm text-gray-500">
                <div className="w-5 h-5 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 font-bold text-[10px]">1</div>
                Be as descriptive as possible in your technical explanations.
              </li>
              <li className="flex gap-3 text-sm text-gray-500">
                <div className="w-5 h-5 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 font-bold text-[10px]">2</div>
                Focus on core concepts and best practices.
              </li>
              <li className="flex gap-3 text-sm text-gray-500">
                <div className="w-5 h-5 rounded-full bg-blue-50 text-blue-600 flex items-center justify-center flex-shrink-0 font-bold text-[10px]">3</div>
                Answers are saved automatically as you move between questions.
              </li>
            </ul>
          </div>

          <div className="premium-card bg-gradient-to-br from-gray-900 to-slate-800 text-white border-none shadow-xl">
            <h3 className="font-bold mb-2 flex items-center gap-2">
              <AlertCircle className="text-yellow-400 w-4 h-4" />
              Proctoring Status
            </h3>
            <p className="text-xs text-slate-400 mb-6 leading-relaxed">
              Real-time monitoring is disabled for Phase 1. Complete this stage to unlock AI Surveillance.
            </p>
            <div className="space-y-3">
              <div className="flex items-center justify-between text-[10px] uppercase font-bold tracking-widest text-slate-500">
                <span>Phase Progress</span>
                <span>25%</span>
              </div>
              <div className="w-full h-1 bg-slate-700 rounded-full overflow-hidden">
                <div className="h-full bg-blue-500 w-1/4"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interview;

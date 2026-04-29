import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
from .state import InterviewState

llm_fast = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.1,
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

# --- LOWER LEVEL AGENTS (Specialists) ---

def technical_specialist_node(state: InterviewState):
    """Analyzes technical correctness and depth."""
    transcript = state.get("transcript", [])
    if not transcript or transcript[-1]["role"] != "human": return {}
    
    latest_answer = transcript[-1]["content"]
    question = state.get("current_question", "")
    
    prompt = f"Assess the technical accuracy of this answer for the question: {question}. Answer: {latest_answer}. Rate 0-100 and list missing technical concepts."
    response = llm_fast.invoke([SystemMessage(content=prompt)])
    
    return {"technical_audit": response.content}

def soft_skills_specialist_node(state: InterviewState):
    """Analyzes communication, tone, and confidence."""
    transcript = state.get("transcript", [])
    if not transcript or transcript[-1]["role"] != "human": return {}
    
    latest_answer = transcript[-1]["content"]
    
    prompt = f"Analyze the communication style, clarity, and tone of this answer: {latest_answer}. Rate 0-100."
    response = llm_fast.invoke([SystemMessage(content=prompt)])
    
    return {"soft_skills_audit": response.content}

# --- MEDIUM LEVEL AGENTS (Consolidators) ---

def internal_review_node(state: InterviewState):
    """Consolidates audits into a structured report."""
    tech_audit = state.get("technical_audit", "N/A")
    soft_audit = state.get("soft_skills_audit", "N/A")
    
    prompt = f"""Summarize these two audits into a final performance report:
    Technical Audit: {tech_audit}
    Soft Skills Audit: {soft_audit}
    
    Return JSON: {{"overall_score": 0, "summary": "", "recommendation": ""}}"""
    
    response = llm_fast.invoke([SystemMessage(content=prompt)])
    # Parsing logic here...
    try:
        content = response.content.strip().replace('```json', '').replace('```', '')
        summary = json.loads(content)
        return {"scores": {"overall_grade": summary.get("overall_score", 0)}, "summary": summary.get("summary")}
    except:
        return {"summary": "Review complete"}

# --- HIGHER LEVEL AGENT (The Director/Hiring Manager) ---

def senior_manager_node(state: InterviewState):
    """Makes the final decision on the session state."""
    summary = state.get("summary", "")
    # Senior Manager logic to decide if the interview should end or continue with higher difficulty
    return {"manager_notes": f"Reviewed summary: {summary[:100]}..."}

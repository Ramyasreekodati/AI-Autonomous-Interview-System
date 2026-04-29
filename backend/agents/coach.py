import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
from .state import InterviewState

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.5,
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

def coach_node(state: InterviewState):
    """
    The Coach Agent provides constructive feedback and improvement tips.
    """
    transcript = state.get("transcript", [])
    scores = state.get("scores", {})
    
    if not transcript or transcript[-1]["role"] != "human":
        return {}

    latest_answer = transcript[-1]["content"]
    question = state.get("current_question", "General Introduction")
    
    system_prompt = f"""You are an expert Interview Coach. 
Analyze the candidate's last answer and provide one specific, actionable coaching tip.
Focus on how they can improve their technical depth, structure (using STAR), or delivery.

Keep it encouraging but professional.
Format: One short paragraph (max 2 sentences).
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Question: {question}\nAnswer: {latest_answer}\nCurrent Scores: {json.dumps(scores)}")
    ]
    
    try:
        response = llm.invoke(messages)
        tip = response.content.strip()
        
        # Add the tip to the state (we might need to update InterviewState to hold a 'coaching_tip' field)
        return {"coaching_tip": tip}
    except Exception as e:
        print(f"Coach error: {e}")
        return {}

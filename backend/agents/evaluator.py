import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import json
from .state import InterviewState

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2, # Lower temperature for more consistent grading
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

def evaluator_node(state: InterviewState):
    """
    The Evaluator Agent runs asynchronously/after the human answers.
    It looks at the latest answer and updates the scores.
    """
    transcript = state.get("transcript", [])
    current_scores = state.get("scores", {})
    
    # We only want to evaluate if the last message was from the human
    if not transcript or transcript[-1]["role"] != "human":
        return {"scores": current_scores}
        
    latest_answer = transcript[-1]["content"]
    question = state.get("current_question", "General Introduction")
    
    system_prompt = f"""You are an expert AI Interview Evaluator.
You need to evaluate the candidate's latest answer to the following question:
Question: {question}

Provide a JSON output with the following format, evaluating out of 100:
{{
    "technical_accuracy": 85,
    "communication_clarity": 90,
    "relevance": 80,
    "filler_words_count": 2,
    "tone": "Confident",
    "feedback_notes": "Good answer, but could use more specific examples."
}}
Return ONLY valid JSON.
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=f"Candidate's Answer: {latest_answer}")
    ]
    
    try:
        response = llm.invoke(messages)
        # Strip markdown json formatting if present
        content = response.content.strip().replace('```json', '').replace('```', '')
        evaluation = json.loads(content)
        
        # Calculate new moving averages or just store the latest
        new_scores = {
            "technical": evaluation.get("technical_accuracy", 80),
            "communication": evaluation.get("communication_clarity", 80),
            "relevance": evaluation.get("relevance", 80),
            "filler_words": evaluation.get("filler_words_count", 0),
            "tone": evaluation.get("tone", "Neutral")
        }
        
        # We can calculate an overall confidence/grade score here
        avg_score = (new_scores["technical"] + new_scores["communication"] + new_scores["relevance"]) / 3
        new_scores["overall_grade"] = avg_score
        
        # 🎮 Gamification: Bronze / Silver / Gold Badges
        if avg_score >= 90:
            new_scores["badge"] = "Gold 🏆"
        elif avg_score >= 75:
            new_scores["badge"] = "Silver 🥈"
        else:
            new_scores["badge"] = "Bronze 🥉"
        
        return {"scores": new_scores}
        
    except Exception as e:
        print(f"Evaluator error: {e}")
        return {"scores": current_scores}

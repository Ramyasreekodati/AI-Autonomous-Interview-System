import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
from .state import InterviewState

# Initialize the Gemini model for the interviewer
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.7,
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

def interviewer_node(state: InterviewState):
    """
    The Interviewer Agent is responsible for asking questions and keeping the conversation flowing.
    """
    job_role = state.get("job_role", "General")
    transcript = state.get("transcript", [])
    question_count = state.get("question_count", 0)
    
    # Base system prompt with Indian Market Localization
    system_prompt = f"""You are a Senior Technical Recruiter at a top-tier Indian tech company (e.g., TCS, Infosys, Wipro, or FAANG India) conducting a mock interview for a {job_role} position.
Your goal is to assess the candidate's skills, ask highly relevant questions, and provide a realistic interview experience tailored to the competitive Indian job market.

Rules:
1. Keep your responses concise and conversational (1-2 sentences max).
2. Ask one question at a time. Do NOT ask multiple questions at once.
3. Test for both technical depth and cultural competencies expected in Indian tech hubs (e.g., handling high-pressure deadlines, cross-timezone collaboration, and resourcefulness).
4. Occasionally ask standard scenario questions favored by Indian product and service companies (e.g., "Explain a complex system you designed from scratch").
5. If this is the start of the interview, greet them professionally and ask the first question.
6. If they just answered, acknowledge their answer briefly and ask a relevant follow-up or move to the next topic.
"""
    
    messages = [SystemMessage(content=system_prompt)]
    
    # Append conversation history
    for msg in transcript:
        if msg["role"] == "ai":
            messages.append(SystemMessage(content=msg["content"])) # We treat previous AI as context
        elif msg["role"] == "human":
            messages.append(HumanMessage(content=msg["content"]))
            
    # Generate the next response/question
    response = llm.invoke(messages)
    
    new_message = {"role": "ai", "content": response.content}
    
    return {
        "transcript": [new_message],
        "current_question": response.content,
        "question_count": question_count + 1
    }

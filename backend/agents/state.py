from typing import TypedDict, List, Annotated, Dict
import operator

class InterviewState(TypedDict):
    candidate_id: str
    candidate_name: str
    job_role: str
    difficulty: str
    # transcript will be a list of dictionaries like {"role": "ai/human", "content": "..."}
    # operator.add ensures that when we return a new list, it appends to the existing one
    transcript: Annotated[List[Dict[str, str]], operator.add]
    current_question: str
    question_count: int
    # Scores for different metrics (e.g., confidence, technical, pace)
    scores: dict
    coaching_tip: str
    technical_audit: str
    soft_skills_audit: str
    summary: str
    manager_notes: str
    # Any proctoring alerts detected during the session
    proctoring_alerts: Annotated[List[str], operator.add]
    # Status of the interview (e.g., 'in_progress', 'completed')
    status: str

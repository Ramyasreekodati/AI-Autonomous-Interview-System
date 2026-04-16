from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    text: str
    category: str

class Question(QuestionBase):
    id: int
    class Config:
        from_attributes = True

class CandidateCreate(BaseModel):
    name: str
    email: str
    password: str

class InterviewBase(BaseModel):
    candidate_email: str

class Interview(BaseModel):
    id: int
    status: str
    class Config:
        from_attributes = True

class InterviewStart(BaseModel):
    candidate_name: str
    candidate_email: str
    role: str
    skills: List[str]
    difficulty: str
    num_questions: Optional[int] = 5

class ResponseCreate(BaseModel):
    question_id: int
    answer_text: str

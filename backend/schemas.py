from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class QuestionBase(BaseModel):
    text: str
    category: str

class Question(QuestionBase):
    id: int
    class Config:
        orm_mode = True

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
        orm_mode = True

class ResponseCreate(BaseModel):
    question_id: int
    answer_text: str

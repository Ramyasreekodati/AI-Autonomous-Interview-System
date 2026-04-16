from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Float, JSON
from sqlalchemy.orm import relationship
from database import Base
import datetime

class Candidate(Base):
    __tablename__ = "candidates"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    interviews = relationship("Interview", back_populates="candidate")

class Interview(Base):
    __tablename__ = "interviews"
    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    start_time = Column(DateTime, default=datetime.datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="pending")  # pending, ongoing, completed
    total_score = Column(Float, default=0.0)
    risk_level = Column(String, default="low")
    candidate = relationship("Candidate", back_populates="interviews")
    responses = relationship("Response", back_populates="interview")
    alerts = relationship("Alert", back_populates="interview")

class Question(Base):
    __tablename__ = "questions"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"), nullable=True) # Associated interview
    text = Column(String)
    category = Column(String)
    difficulty = Column(String)

class Response(Base):
    __tablename__ = "responses"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    answer_text = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    sentiment_score = Column(Float, default=0.0)
    relevance_score = Column(Float, default=0.0)
    interview = relationship("Interview", back_populates="responses")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id"))
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    alert_type = Column(String)  # face_not_detected, multiple_faces, phone_detected, etc.
    severity = Column(String)  # low, medium, high
    interview = relationship("Interview", back_populates="alerts")

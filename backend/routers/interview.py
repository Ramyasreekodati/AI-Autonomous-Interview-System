from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Header
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session
from database import get_db
import models, schemas
from services.ai_engine import ai_engine
from services.scoring import scoring_service
from services.auth import auth_service
import os
import datetime
from typing import List

router = APIRouter(prefix="/interview", tags=["interview"])

def get_current_interview(authorization: str = Header(...)):
    token = authorization.replace("Bearer ", "")
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session token")
    return payload["interview_id"]

@router.post("/start")
def start_interview(data: schemas.InterviewStart, db: Session = Depends(get_db)):
    candidate = db.query(models.Candidate).filter(models.Candidate.email == data.candidate_email).first()
    if not candidate:
        candidate = models.Candidate(name=data.candidate_name, email=data.candidate_email)
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
    
    interview = models.Interview(
        candidate_id=candidate.id, 
        status="ongoing",
        target_role=data.role,
        target_skills=", ".join(data.skills) if isinstance(data.skills, list) else data.skills,
        experience_level=data.experience,
        infinite_mode=data.infinite_mode,
        adaptive_mode=data.adaptive_mode
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    # If not in adaptive/infinite mode, pre-generate questions
    if not (data.adaptive_mode or data.infinite_mode):
        questions_list = ai_engine.generate_questions(
            role=data.role, 
            skills=data.skills, 
            difficulty=data.difficulty,
            count=data.num_questions,
            experience=data.experience,
            interview_type=data.interview_type,
            style=data.style
        )
        for q_text in questions_list:
            question = models.Question(interview_id=interview.id, text=q_text, category=data.role, difficulty=data.difficulty)
            db.add(question)
        db.commit()
    else:
        # Generate the first question dynamically
        q_text = ai_engine.generate_next_dynamic_question(
            role=data.role,
            skills=data.skills,
            experience=data.experience,
            adaptive=data.adaptive_mode
        )
        question = models.Question(interview_id=interview.id, text=q_text, category=data.role, difficulty="Adaptive")
        db.add(question)
        db.commit()
    
    # Generate access token for the session
    token = auth_service.create_access_token({"interview_id": interview.id})

    return {
        "interview_id": interview.id, 
        "access_token": token,
        "status": "started"
    }

@router.get("/{interview_id}/next-question")
def get_next_dynamic_question(interview_id: int, db: Session = Depends(get_db), current_id: int = Depends(get_current_interview)):
    if interview_id != current_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")

    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check if we should stop
    questions = db.query(models.Question).filter(models.Question.interview_id == interview_id).all()
    responses = db.query(models.Response).filter(models.Response.interview_id == interview_id).all()
    
    # If in infinite mode, we only stop if the user clicks "End" (handled by UI)
    # If in fixed mode, check if we reached the limit
    if not interview.infinite_mode and len(questions) >= 5: # Default limit if not infinite
         # This part is simplified; usually we'd use the num_questions from start_interview
         # but we'll let the UI handle the "Finished" state for now.
         pass

    # Gather history for adaptive logic
    history = []
    for q in questions:
        resp = next((r for r in responses if r.question_id == q.id), None)
        if resp:
            history.append((q.text, resp.answer_text, resp.relevance_score))
    
    # Generate next question
    next_q_text = ai_engine.generate_next_dynamic_question(
        role=interview.target_role,
        skills=interview.target_skills,
        experience=interview.experience_level,
        previous_q_and_a=history,
        adaptive=interview.adaptive_mode
    )
    
    new_question = models.Question(
        interview_id=interview.id, 
        text=next_q_text, 
        category=interview.target_role, 
        difficulty="Adaptive" if interview.adaptive_mode else "Standard"
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    
    return {
        "question_id": new_question.id,
        "text": new_question.text,
        "finished": False,
        "total": -1 if interview.infinite_mode else 5
    }

@router.get("/{interview_id}/question/{index}")
async def get_question(interview_id: int, index: int, db: Session = Depends(get_db), current_id: int = Depends(get_current_interview)):
    if interview_id != current_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")
    
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    
    # Check if questions exist
    questions = db.query(models.Question).filter(models.Question.interview_id == interview_id).all()
    if not questions or index >= len(questions):
        # Generate dynamic if needed
        if interview.adaptive_mode:
            try:
                # Use threadpool for blocking AI generation
                new_q = await run_in_threadpool(ai_engine.generate_questions, interview.target_role, interview.target_skills.split(','), 1)
                if new_q:
                    q = models.Question(interview_id=interview_id, text=new_q[0], category="Adaptive", difficulty="Medium")
                    db.add(q)
                    db.commit()
                    return {"id": q.id, "text": q.text, "finished": False}
            except Exception: pass
        return {"finished": True}
    
    q = questions[index]
    return {"id": q.id, "text": q.text, "finished": False}

@router.post("/{interview_id}/submit-response")
async def submit_response(interview_id: int, data: schemas.ResponseSubmit, db: Session = Depends(get_db), current_id: int = Depends(get_current_interview)):
    if interview_id != current_id:
        raise HTTPException(status_code=403, detail="Not authorized for this session")
    
    answer_text = data.answer_text
    question_id = data.question_id
    # Phase 1: Validation
    if not answer_text or len(answer_text.strip()) < 3:
        raise HTTPException(status_code=400, detail="Answer is empty or too short.")

    # Phase 2: AI Evaluation (Run in threadpool to avoid blocking)
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    
    if not question or not interview:
        raise HTTPException(status_code=404, detail="Entity not found")
        
    evaluation = await run_in_threadpool(
        ai_engine.evaluate_answer,
        question.text, 
        answer_text, 
        role=interview.target_role or "Expert",
        skills=[s.strip() for s in (interview.target_skills or "").split(",")]
    )
    
    # Phase 1: Unique Answer Storage (update if exists)
    response = db.query(models.Response).filter(
        models.Response.interview_id == interview_id,
        models.Response.question_id == question_id
    ).first()
    
    if response:
        response.answer_text = answer_text
        response.timestamp = datetime.datetime.utcnow()
        response.relevance_score = evaluation["score"]
    else:
        response = models.Response(
            interview_id=interview_id, 
            question_id=question_id, 
            answer_text=answer_text,
            relevance_score=evaluation["score"]
        )
        db.add(response)
    
    db.commit()
    
    # Phase 2 REQUIREMENT: RETURN ONLY JSON
    return evaluation

@router.post("/{interview_id}/submit-audio")
async def submit_audio_response(interview_id: int, question_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Read audio bytes
    audio_bytes = await file.read()
    
    # Use real AI for transcription
    transcription = ai_engine.transcribe_bytes(audio_bytes)
    
    # Evaluate the transcribed answer
    interview = db.query(models.Interview).filter(models.Interview.id == interview_id).first()
    question = db.query(models.Question).filter(models.Question.id == question_id).first()
    
    evaluation = ai_engine.evaluate_answer(
        question.text if question else "", 
        transcription,
        role=interview.target_role if interview else "Expert",
        skills=[s.strip() for s in (interview.target_skills or "").split(",")] if interview else []
    )
    score = evaluation.get("score", 0)
    
    response = models.Response(
        interview_id=interview_id, 
        question_id=question_id, 
        answer_text=transcription,
        relevance_score=score
    )
    db.add(response)
    db.commit()
    
    return {"transcription": transcription, "score": score}

@router.post("/analyze-resume")
async def analyze_resume(file: UploadFile = File(...), job_description: str = "Generic", db: Session = Depends(get_db)):
    file_bytes = await file.read()
    resume_content = ""

    # Try PDF parsing first
    if file.filename and file.filename.lower().endswith(".pdf"):
        try:
            import io
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            resume_content = " ".join(page.extract_text() or "" for page in reader.pages)
        except Exception:
            pass

    # Fallback: try to decode as plain text (DOCX or TXT)
    if not resume_content.strip():
        try:
            resume_content = file_bytes.decode("utf-8", errors="ignore")
        except Exception:
            resume_content = "Could not extract text from the uploaded file."

    analysis = ai_engine.analyze_resume_v2(resume_content[:4000], job_description)  # cap at 4000 chars
    return analysis


@router.get("/{interview_id}/results")
def get_interview_results(interview_id: int, db: Session = Depends(get_db)):
    results = scoring_service.calculate_unified_score(interview_id, db)
    return results

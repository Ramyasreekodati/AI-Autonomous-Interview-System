import random
import re

class ScoringService:
    def __init__(self):
        # Local knowledge base for concept mapping (Phase 2 & 4)
        self.concept_keywords = {
            "python": ["decorators", "generators", "list comprehensions", "asyncio", "threading", "gil", "multiprocessing"],
            "react": ["hooks", "useeffect", "usestate", "virtual dom", "props", "components", "jsx", "context api"],
            "sql": ["indexing", "joins", "normalization", "transactions", "acid", "select", "where", "group by"],
            "fastapi": ["pydantic", "di", "dependency injection", "async", "await", "endpoints", "router"],
            "ml": ["overfitting", "training", "testing", "validation", "neural networks", "gradient descent", "backpropagation"],
            "javascript": ["typescript", "closures", "event loop", "promises", "callbacks", "es6", "arrow functions"],
            "aws": ["s3", "ec2", "lambda", "cloudwatch", "iam", "rds", "vpc"]
        }

    def evaluate_response(self, answer_text: str, question_text: str, role="Expert", skills=[]):
        """
        UPGRADED AI EVALUATOR: Uses Gemini for high-precision technical auditing.
        """
        # 1. Immediate Nonsense/Length Filter
        ans_clean = answer_text.strip()
        if len(ans_clean) < 15 or len(set(ans_clean)) < 5: # Detect repetitive gibberish
            return {
                "score": 0,
                "keywords_matched": [],
                "missing_concepts": ["Provide a legitimate technical explanation"],
                "strengths": [],
                "weaknesses": ["Response identified as low-quality or non-technical"]
            }

        # 2. AI Semantic Audit (Connect to Engine)
        from .ai_engine import ai_engine
        return ai_engine.evaluate_answer(question_text, answer_text, role, skills)

    @staticmethod
    def calculate_unified_score(interview_id, db):
        import models
        
        responses = db.query(models.Response).filter(models.Response.interview_id == interview_id).all()
        if not responses:
            return {
                "interview_score": 0, "behavior_score": 0, "risk_level": "high",
                "alerts": [], "final_decision": "fail", "justification": "No responses logged for session.",
                "final_aggregate_score": 0
            }
            
        avg_answer_score = sum([r.relevance_score for r in responses]) / len(responses)
        answer_component = avg_answer_score * 10 
        
        alerts = db.query(models.Alert).filter(models.Alert.interview_id == interview_id).all()
        penalty = 0
        alert_types = []
        for alert in alerts:
            alert_types.append(alert.alert_type)
            if alert.severity == "high": penalty += 20
            elif alert.severity == "medium": penalty += 10
            else: penalty += 5
            
        behavior_score = max(0, 100 - penalty)
        final_score = round((answer_component * 0.7) + (behavior_score * 0.3), 1)
        
        risk_level = "low"
        if penalty > 40: risk_level = "high"
        elif penalty > 15: risk_level = "medium"
        
        final_decision = "pass" if final_score >= 60 and risk_level != "high" else "fail"
        
        # AUDITOR FIX: Deterministic Justification
        justification = f"Candidate achieved a technical score of {round(avg_answer_score,1)}/10. "
        if penalty > 0:
            justification += f"However, {len(alerts)} behavioral alerts were logged, indicating potential risk."
        else:
            justification += "Zero behavioral violations detected during the session."

        # Skills Breakdown logic
        skills_breakdown = {}
        for r in responses:
            q = db.query(models.Question).filter(models.Question.id == r.question_id).first()
            if q:
                cat = q.category or "General"
                if cat not in skills_breakdown:
                    skills_breakdown[cat] = {"score": 0, "count": 0}
                skills_breakdown[cat]["score"] += r.relevance_score
                skills_breakdown[cat]["count"] += 1
        
        # Calculate averages for breakdown
        final_breakdown = {cat: round(data["score"] / data["count"], 1) for cat, data in skills_breakdown.items()}

        return {
            "interview_score": round(avg_answer_score, 1),
            "behavior_score": round(behavior_score, 1),
            "risk_level": risk_level,
            "alerts": list(set(alert_types)),
            "final_decision": final_decision,
            "justification": justification,
            "final_aggregate_score": final_score,
            "skills_breakdown": final_breakdown
        }

scoring_service = ScoringService()

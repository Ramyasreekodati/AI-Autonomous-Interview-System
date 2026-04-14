import random

class ScoringService:
    @staticmethod
    def evaluate_response(answer_text, question_text):
        # In production, use a transformer model to compare answer with expected answer
        # For this demo, we'll return a score based on length and some keywords
        score = min(len(answer_text) / 100, 1.0) * 100
        sentiment = 0.8 # Placeholder
        return score, sentiment

    @staticmethod
    def calculate_unified_score(interview_id, db):
        import models
        
        # 1. Interview Response Score (Avg of response relevance scores)
        responses = db.query(models.Response).filter(models.Response.interview_id == interview_id).all()
        interview_score = sum([r.relevance_score for r in responses]) / len(responses) if responses else 0
        
        # 2. Behavioral Score (Starts at 100, drops per alert)
        alerts = db.query(models.Alert).filter(models.Alert.interview_id == interview_id).all()
        # High severity alerts drop 10 points, medium 5 points
        penalty = sum([10 if a.severity == "high" else 5 for a in alerts])
        behavior_score = max(0, 100 - penalty)
        
        # 3. Final Risk Level
        risk_level = "Low"
        if penalty > 30: risk_level = "High"
        elif penalty > 10: risk_level = "Medium"
        
        # 4. Total Aggregate Score (Weighted 70% Interview, 30% Behavior)
        total_score = (interview_score * 0.7) + (behavior_score * 0.3)
        
        return {
            "interview_score": round(interview_score, 2),
            "behavior_score": round(behavior_score, 2),
            "total_score": round(total_score, 2),
            "risk_level": risk_level,
            "alert_count": len(alerts)
        }

    @staticmethod
    def calculate_final_score(interview_id, db_session):
        pass

scoring_service = ScoringService()

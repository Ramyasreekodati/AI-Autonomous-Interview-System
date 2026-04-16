import random

class ScoringService:
    @staticmethod
    def evaluate_response(answer_text, question_text):
        # Phase 2: Evaluation Engine (No Hallucination)
        # Rules: If answer invalid -> score = 0, NO inventions, STICK to given input.
        
        # Simple Validation (Part of Phase 1 but reinforced here)
        if not answer_text or len(answer_text.strip()) < 10:
            return {
                "score": 0,
                "keywords_matched": [],
                "missing_concepts": ["The answer was too short or non-existent."],
                "strengths": [],
                "weaknesses": ["Lack of information provided."]
            }

        # In a real system, this would be an LLM analyzing the answer against the question.
        # Here we use a rule-based simulation that matches Phase 2 requirements.
        
        # Define some keywords based on the question text (simple heuristic)
        # We extract potential keywords from the question to check if they are addressed
        potential_keywords = [word.lower() for word in question_text.split() if len(word) > 4]
        
        matched = []
        missing = []
        for kw in potential_keywords:
            if kw in answer_text.lower():
                matched.append(kw)
            else:
                missing.append(kw)
        
        # Extract strengths/weaknesses strictly from the input
        strengths = []
        weaknesses = []
        
        if len(answer_text) > 100:
            strengths.append("Detailed explanation provided.")
        if matched:
            strengths.append(f"Successfully addressed {len(matched)} key concepts from the question.")
        
        if len(missing) > 2:
            weaknesses.append("Several technical aspects of the question were not explicitly covered.")
        if len(answer_text) < 50:
            weaknesses.append("Response is somewhat brief.")

        # Scoring Logic (0-10)
        base_score = min(len(matched) * 2, 7) # Max 7 for matching
        detail_score = min(len(answer_text) // 50, 3) # Max 3 for detail
        final_score = base_score + detail_score
        
        return {
            "score": round(final_score, 1),
            "keywords_matched": list(set(matched)),
            "missing_concepts": list(set(missing[:3])), # Limit to realistic missing parts
            "strengths": list(set(strengths)),
            "weaknesses": list(set(weaknesses))
        }

    @staticmethod
    def calculate_unified_score(interview_id, db):
        import models
        
        # 1. Answer Evaluation (70% weight)
        responses = db.query(models.Response).filter(models.Response.interview_id == interview_id).all()
        if not responses:
            return {"error": "No responses found for this interview."}
            
        avg_answer_score = sum([r.relevance_score for r in responses]) / len(responses)
        # Convert 0-10 scale to 0-100 for internal math
        answer_component = avg_answer_score * 10 
        
        # 2. Behavior & Proctoring (30% weight)
        alerts = db.query(models.Alert).filter(models.Alert.interview_id == interview_id).all()
        
        # Base behavior score is 100
        # Deduct based on severity
        penalty = 0
        alert_types = []
        for alert in alerts:
            alert_types.append(alert.alert_type)
            if alert.severity == "high": penalty += 15
            elif alert.severity == "medium": penalty += 10
            else: penalty += 5
            
        behavior_score = max(0, 100 - penalty)
        
        # 3. Final Integration Logic
        # Final Score = 70% answer quality + 30% behavior
        final_score = (answer_component * 0.7) + (behavior_score * 0.3)
        
        # 4. Final Decision & Risk Level
        risk_level = "low"
        if penalty > 40: risk_level = "high"
        elif penalty > 15: risk_level = "medium"
        
        final_decision = "pass" if final_score >= 60 and risk_level != "high" else "fail"
        
        # 5. Justification (Strictly based on data)
        just_parts = []
        just_parts.append(f"Answer quality averaged {round(avg_answer_score, 1)}/10.")
        if behavior_score < 80:
            just_parts.append(f"Behavioral flags detected (Penalty: {penalty}).")
        else:
            just_parts.append("Candidate maintained high integrity throughout.")
            
        if "phone_detected" in alert_types:
            just_parts.append("Critical violation: Phone detected.")
            
        justification = " ".join(just_parts)

        return {
            "interview_score": round(avg_answer_score, 1),
            "behavior_score": round(behavior_score, 1),
            "risk_level": risk_level,
            "alerts": list(set(alert_types)),
            "final_decision": final_decision,
            "justification": justification,
            "final_aggregate_score": round(final_score, 1)
        }

scoring_service = ScoringService()

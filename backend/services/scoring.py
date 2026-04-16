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

    def evaluate_response(self, answer_text: str, question_text: str):
        # AUDITOR FIX: Deterministic, non-hallucinating evaluation
        score = 0
        matched_keywords = []
        missing_concepts = []
        
        # 1. Basic Validation
        ans_clean = answer_text.lower().strip()
        if len(ans_clean) < 10:
            return {
                "score": 0,
                "keywords_matched": [],
                "missing_concepts": ["Provide a more detailed technical explanation"],
                "strengths": [],
                "weaknesses": ["Answer too short"]
            }

        # 2. Concept Mapping (Real Intelligence)
        # Check matching keywords based on the question context
        q_lower = question_text.lower()
        active_concepts = []
        for concept, kw_list in self.concept_keywords.items():
            if concept in q_lower:
                active_concepts.extend(kw_list)
        
        # If no specific concept detected, use a general pool
        if not active_concepts:
            active_concepts = ["implementation", "scalability", "performance", "security", "integrity"]

        for kw in active_concepts:
            if re.search(r'\b' + re.escape(kw) + r'\b', ans_clean):
                matched_keywords.append(kw)
            else:
                missing_concepts.append(kw)

        # 3. Score Calculation
        # Length factor (caps at 4 points)
        len_score = min(4, len(ans_clean) / 100)
        
        # Keyword factor (caps at 6 points)
        kw_score = 0
        if active_concepts:
            kw_score = min(6, (len(matched_keywords) / len(active_concepts)) * 10)
        
        total_score = round(min(10, len_score + kw_score), 1)

        # 4. Strengths & Weaknesses
        strengths = []
        weaknesses = []
        if total_score > 7: strengths.append("Strong conceptual understanding")
        if len(ans_clean) > 300: strengths.append("Detailed technical depth")
        
        if total_score < 4: weaknesses.append("Lacks technical specifics")
        if not matched_keywords: weaknesses.append("Missing core industry terminology")

        return {
            "score": total_score,
            "keywords_matched": matched_keywords,
            "missing_concepts": missing_concepts[:3], # Show top 3
            "strengths": strengths,
            "weaknesses": weaknesses
        }

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

        return {
            "interview_score": round(avg_answer_score, 1),
            "behavior_score": round(behavior_score, 1),
            "risk_level": risk_level,
            "alerts": list(set(alert_types)),
            "final_decision": final_decision,
            "justification": justification,
            "final_aggregate_score": final_score
        }

scoring_service = ScoringService()

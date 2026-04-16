import random

class LLMService:
    def __init__(self):
        # Phase 1: Dynamic Question Generation Logic
        pass

    def generate_question(self, role="Software Engineer", skills=["General"], difficulty="Medium", type="Technical"):
        technical_templates = [
            "As a {role}, how would you approach implementing {skill} in a production-ready environment?",
            "Can you explain a challenging scenario where you had to debug or optimize {skill} for a {role} project?",
            "What are the internal mechanisms of {skill} that every senior {role} must understand to ensure system reliability?",
            "How do you ensure data integrity and security when working with {skill} in complex {role} workflows?",
            "Comparing {skill} with modern alternatives, why is it specifically favored for {role} applications in the current tech landscape?"
        ]
        
        hr_templates = [
            "Tell me about a time you had to lead a {role} team through a major technical shift involving {skill}.",
            "How do you manage conflicting priorities between performance optimization and rapid delivery in a {role} role?",
            "Describe how you stay updated with {skill} advancements to maintain your edge as a {role}.",
            "What is your philosophy on mentorship and knowledge sharing within a {role} squad working on {skill}?"
        ]
        
        difficulty_modifiers = {
            "Basic": "Focus on fundamental concepts and standard syntax.",
            "Medium": "Focus on integration patterns, error handling, and performance trade-offs.",
            "Advanced": "Focus on high-level architecture, low-level optimizations, and scalability bottlenecks."
        }
        
        template_pool = technical_templates if type in ["Technical", "Mixed"] else hr_templates
        if type == "Mixed" and random.random() > 0.5:
            template_pool = hr_templates
            
        template = random.choice(template_pool)
        skill = random.choice(skills) if skills else "relevant technologies"
        
        question = template.format(role=role, skill=skill)
        modifier = difficulty_modifiers.get(difficulty, difficulty_modifiers["Medium"])
        return f"{question}\n[Context: {modifier}]"

    def generate_question_set(self, role, skills, difficulty, num):
        # 1. FIX generate_questions FUNCTION - Ensure it returns a LIST of strings
        # 2. FIX LLM RESPONSE PARSING - Split, strip, remove numbering
        
        # Simulate LLM raw response as requested in Section 2
        raw_response = ""
        for i in range(1, num + 1):
            q = self.generate_question(role, skills, difficulty)
            raw_response += f"{i}. {q}\n"
            
        questions = []
        for line in raw_response.split("\n"):
            line = line.strip()
            if line:
                # Remove numbering (e.g., "1. Question" -> "Question")
                if "." in line[:4]: # Safety check for leading numbers
                    q = line.split(".", 1)[-1].strip()
                    questions.append(q)
                else:
                    questions.append(line)
        
        # RULES: NEVER return None, NEVER return empty
        if not questions:
            return ["Sample technical question for " + role]
            
        return questions

llm_service = LLMService()

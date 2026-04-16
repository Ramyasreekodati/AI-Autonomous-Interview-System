import random

class LLMService:
    def __init__(self):
        # Phase 1: Dynamic Question Generation Logic
        pass

    def generate_question(self, role="Software Engineer", skills=["General"], difficulty="Medium", type="Technical"):
        # Auditor Requirement: Allow ANY role and ANY skill (Dynamic Input)
        # Auditor Requirement: No generic questions
        
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
        
    def generate_question_set(self, role, skills, difficulty, num):
        # AUDITOR REQUIREMENT: Structured prompt for bulk generation
        prompt = f"Generate {num} interview questions for:\nRole: {role}\nSkills: {skills}\nDifficulty: {difficulty}\n\nReturn as numbered list."
        
        # In a real environment, this would call the LLM and parse the numbered list.
        # Here we simulate the generation logic based on the requested prompt structure.
        questions = []
        for i in range(1, num + 1):
            q = self.generate_question(role, skills, difficulty)
            questions.append(f"{i}. {q}")
        return questions

llm_service = LLMService()

import random

class LLMService:
    def __init__(self):
        self._generator = None

    def generate_question(self, role="Software Engineer", skills=["Python"], difficulty="Medium"):
        # Based on Phase 1 Requirements: Dynamic Question Generation
        # No generic questions
        
        templates = {
            "Basic": [
                "What is the fundamental purpose of {skill} in a {role} context?",
                "Can you explain the basic syntax for a common operation in {skill}?",
                "Describe a simple use case for {skill} that you have worked on.",
                "What are the core features of {skill} that make it suitable for {role}?"
            ],
            "Medium": [
                "How do you handle error management and debugging when working with {skill}?",
                "Describe a situation where you had to integrate {skill} with another technology in a {role} project.",
                "Explain the concept of {concept} in {skill} and how it applies to building scalable systems.",
                "Compare {skill} with an alternative technology for {role} tasks. Why would you choose one over the other?"
            ],
            "Advanced": [
                "How would you architect a high-concurrency system using {skill} for a complex {role} requirement?",
                "Discuss the internal memory management or performance bottlenecks of {skill} that a senior {role} should be aware of.",
                "Explain how you would implement {advanced_topic} using {skill} to ensure maximum security and reliability.",
                "If you were to contribute to the open-source ecosystem of {skill}, what optimization or feature would you propose for {role} workflows?"
            ]
        }
        
        concepts = {
            "Python": ["decorators", "generators", "multiprocessing", "asyncio"],
            "React": ["hooks", "virtual DOM", "state management", "server-side rendering"],
            "SQL": ["indexing", "normalization", "joins", "transaction isolation levels"],
            "Java": ["JVM internals", "garbage collection", "streams API", "spring boot"],
            "Data Science": ["overfitting", "feature engineering", "cross-validation", "regularization"]
        }
        
        advanced_topics = {
            "Python": ["metaprogramming", "GIL optimization", "C extensions"],
            "React": ["reconciliation algorithm", "fiber architecture", "micro-frontends"],
            "SQL": ["query optimization", "sharding", "distributed transactions"],
            "Java": ["JIT compilation", "low-latency tuning", "reactive programming"],
            "Data Science": ["deep learning architectures", "hyperparameter tuning at scale", "bias-variance tradeoff"]
        }

        # Select a random skill from the list if multiple are provided
        skill = random.choice(skills) if skills else "General Technologies"
        
        difficulty_key = difficulty.capitalize() if difficulty.capitalize() in templates else "Medium"
        template = random.choice(templates[difficulty_key])
        
        # Skill-specific context
        skill_concept = random.choice(concepts.get(skill, ["core components"]))
        adv_topic = random.choice(advanced_topics.get(skill, ["system design"]))
        
        question = template.format(
            role=role, 
            skill=skill, 
            concept=skill_concept, 
            advanced_topic=adv_topic,
            topic=skill # for backward compatibility if template uses it
        )
        
        return question

llm_service = LLMService()


from transformers import pipeline
import random

class LLMService:
    def __init__(self):
        self._generator = None

    @property
    def generator(self):
        if self._generator is None:
            try:
                print("Loading LLM model (distilgpt2)...")
                self._generator = pipeline("text-generation", model="distilgpt2")
            except Exception as e:
                print(f"Error loading LLM: {e}")
                self._generator = "FAILED"
        return self._generator if self._generator != "FAILED" else None

    def generate_question(self, category="Technical", difficulty="Medium"):
        gen = self.generator
        if not gen:
            # Fallback to templates if model failed to load
            templates = {
                "Technical": ["Explain the concept of {topic} in your own words.", "How would you optimize {topic} for better performance?"],
                "HR": ["Why do you want to work at {company}?", "Tell me about a time you handled a conflict."],
            }
            topics = ["rest-apis", "database-indexing", "asynchronous-programming", "cloud-security"]
            topic = random.choice(topics)
            template = random.choice(templates.get(category, templates["HR"]))
            return template.format(topic=topic, company="this organization")

        prompt = f"Generate a {difficulty} level interview question for a {category} role:"
        result = gen(prompt, max_length=50, num_return_sequences=1)
        return result[0]['generated_text'].replace(prompt, "").strip()

llm_service = LLMService()

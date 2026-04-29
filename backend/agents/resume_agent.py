import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage

llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.2,
    google_api_key=os.environ.get("GEMINI_API_KEY")
)

def analyze_resume(resume_text: str, job_description: str) -> dict:
    """
    Analyzes a resume against a job description for ATS optimization.
    """
    system_prompt = """You are an expert ATS (Applicant Tracking System) Analyzer.
Your task is to analyze the provided resume against the provided Job Description.

Return ONLY a valid JSON object with the following schema:
{
    "ats_keyword_match": 72, 
    "formatting_score": 95,
    "insight": "Your 'Skills' section is well-structured. Consider adding more metrics.",
    "missing_keywords": ["Kubernetes", "GraphQL", "Agile"]
}
Note: the scores should be integers out of 100.
"""

    human_prompt = f"Job Description:\n{job_description}\n\nResume Text:\n{resume_text}"

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=human_prompt)
    ]

    try:
        response = llm.invoke(messages)
        content = response.content.strip().replace('```json', '').replace('```', '')
        return json.loads(content)
    except Exception as e:
        print(f"Resume Agent Error: {e}")
        return {
            "ats_keyword_match": 50,
            "formatting_score": 50,
            "insight": "Error analyzing resume.",
            "missing_keywords": []
        }

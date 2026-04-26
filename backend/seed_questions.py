import sqlite3
import os

db_path = "c:\\Users\\Lenovo\\Desktop\\ai interview\\AI-Autonomous-Interview-System\\backend\\interview_system_v3.db"

questions = [
    # Software Engineering - Behavioral
    ("Tell me about a time you had to deal with a difficult teammate.", "Software Engineering", "Medium"),
    ("What is your biggest technical accomplishment?", "Software Engineering", "Hard"),
    ("How do you stay updated with new technologies?", "Software Engineering", "Easy"),
    ("Tell me about a time you failed and how you handled it.", "Software Engineering", "Medium"),
    ("Why do you want to work for this company?", "Software Engineering", "Easy"),
    
    # Software Engineering - Technical
    ("Explain the difference between a process and a thread.", "Software Engineering", "Medium"),
    ("What are the SOLID principles?", "Software Engineering", "Hard"),
    ("How does a hash table work under the hood?", "Software Engineering", "Medium"),
    ("What is the difference between SQL and NoSQL?", "Software Engineering", "Easy"),
    ("Explain the concept of Big O notation.", "Software Engineering", "Medium"),
    
    # Data Science
    ("What is the difference between supervised and unsupervised learning?", "Data Science", "Easy"),
    ("How do you handle missing values in a dataset?", "Data Science", "Medium"),
    ("Explain the Bias-Variance tradeoff.", "Data Science", "Hard"),
    ("What is a confusion matrix?", "Data Science", "Easy"),
    ("How does Random Forest work?", "Data Science", "Medium"),
    
    # Product Management
    ("How do you prioritize features for a new product?", "Product Management", "Medium"),
    ("Tell me about a product you love and how you would improve it.", "Product Management", "Easy"),
    ("How do you handle stakeholders with conflicting interests?", "Product Management", "Hard"),
    ("What is an MVP?", "Product Management", "Easy"),
    ("How do you measure the success of a new feature?", "Product Management", "Medium"),
    
    # STAR Method Specific
    ("Describe a Situation where you had to make a quick decision.", "Behavioral", "Medium"),
    ("What was the Task at hand when you led your last project?", "Behavioral", "Medium"),
    ("What specific Actions did you take to resolve a conflict?", "Behavioral", "Hard"),
    ("What was the Result of your optimization work?", "Behavioral", "Medium"),
]

def seed_db():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Clear existing questions to avoid duplicates for this seed
    cursor.execute("DELETE FROM questions")
    
    cursor.executemany(
        "INSERT INTO questions (text, category, difficulty) VALUES (?, ?, ?)",
        questions
    )
    
    conn.commit()
    print(f"✅ Seeded {len(questions)} high-quality questions into the database.")
    conn.close()

if __name__ == "__main__":
    seed_db()

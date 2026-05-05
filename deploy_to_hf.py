from huggingface_hub import HfApi
import os

api = HfApi()
token = 'hf_fnsGidUcemhsdSxpEFJbSxFBJXtsiEqcR0'
repo_id = 'kodatiramyasree/recruit-ai'

files_to_upload = [
    'Dockerfile', 
    'backend/requirements.txt', 
    'backend/main.py', 
    'backend/database.py', 
    'backend/models.py', 
    'backend/routers/auth.py', 
    'backend/routers/interview.py', 
    'backend/routers/recruiter.py', 
    'backend/services/ai_engine.py', 
    'backend/services/reporting.py', 
    'backend/services/scoring.py', 
    'backend/services/surveillance.py', 
    'backend/agents/state.py', 
    'backend/agents/orchestrator.py', 
    'backend/agents/evaluator.py', 
    'backend/agents/evaluator_hierarchy.py', 
    'backend/agents/interviewer.py', 
    'backend/agents/coach.py', 
    'backend/agents/resume_agent.py', 
    'backend/agents/__init__.py', 
    'README.md'
]

# Upload core files
for f in files_to_upload:
    if os.path.exists(f):
        print(f"Uploading {f}...")
        api.upload_file(
            path_or_fileobj=f, 
            path_in_repo=f, 
            repo_id=repo_id, 
            repo_type="space", 
            token=token
        )

# Upload frontend dist folder (recursively)
frontend_dist = 'frontend/dist'
if os.path.exists(frontend_dist):
    print("Uploading frontend/dist folder...")
    api.upload_folder(
        folder_path=frontend_dist,
        path_in_repo='frontend/dist',
        repo_id=repo_id,
        repo_type='space',
        token=token
    )

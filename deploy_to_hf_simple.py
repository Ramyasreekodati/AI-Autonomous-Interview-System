from huggingface_hub import HfApi
import os

api = HfApi()
token = 'hf_fnsGidUcemhsdSxpEFJbSxFBJXtsiEqcR0'
repo_id = 'kodatiramyasree/recruit-ai'

files = [
    'Dockerfile', 
    'backend/requirements.txt', 
    'backend/main.py', 
    'backend/database.py', 
    'backend/models.py',
    'README.md'
]

for f in files:
    if os.path.exists(f):
        try:
            print(f"Uploading {f}...")
            api.upload_file(
                path_or_fileobj=f,
                path_in_repo=f,
                repo_id=repo_id,
                repo_type='space',
                token=token
            )
        except Exception as e:
            print(f"Failed to upload {f}: {e}")

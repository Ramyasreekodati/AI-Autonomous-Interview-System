import os
import sys
import uuid

backend_path = os.path.abspath("backend")
print(f"Backend path: {backend_path}")
if backend_path not in sys.path:
    sys.path.append(backend_path)
    print("Added backend to sys.path")

try:
    from services.ai_engine import ai_engine
    print("Imported ai_engine")
    from services.surveillance import surveillance
    print("Imported surveillance")
    from services.stt import stt_service
    print("Imported stt_service")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Exception: {e}")

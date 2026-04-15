import sys
import os
sys.path.append(os.getcwd())

print("Testing imports...")
try:
    from routers import interview, auth
    print("Routers imported")
    from services.surveillance import surveillance
    print("Surveillance imported")
    from database import get_db
    print("Database imported")
    import models
    print("Models imported")
    from services.reporting import reporting_service
    print("Reporting imported")
except Exception as e:
    print(f"Error importing: {e}")
    import traceback
    traceback.print_exc()

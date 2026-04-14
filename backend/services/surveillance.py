import cv2
import mediapipe as mp
import numpy as np
from sqlalchemy.orm import Session
import models
import datetime
from services.object_detection import object_detector

class SurveillanceService:
    def __init__(self):
        try:
            self.mp_face_detection = mp.solutions.face_detection
            self.face_detection = self.mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5)
        except Exception as e:
            print(f"Warning: MediaPipe solutions not found or failing: {e}")
            self.face_detection = None

    def process_frame(self, frame_bytes, interview_id: int, db: Session):
        # Convert bytes to numpy array
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Invalid frame"}

        # Convert to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_detection.process(frame_rgb)
        
        alerts = []
        face_count = 0
        
        # Face Detection
        if self.face_detection:
            results = self.face_detection.process(frame_rgb)
            if results.detections:
                face_count = len(results.detections)
        
        # Phone Detection
        if object_detector.detect_phone(frame):
            alerts.append({"type": "phone_detected", "severity": "high"})

        if face_count == 0:
            alerts.append({"type": "no_face_detected", "severity": "medium"})
        elif face_count > 1:
            alerts.append({"type": "multiple_faces_detected", "severity": "high"})

        # Log alerts to database
        for alert_data in alerts:
            db_alert = models.Alert(
                interview_id=interview_id,
                alert_type=alert_data["type"],
                severity=alert_data["severity"],
                timestamp=datetime.datetime.utcnow()
            )
            db.add(db_alert)
        
        db.commit()

        return {
            "face_count": face_count,
            "alerts": alerts,
            "emotion": "Neutral"  # Placeholder until FER is fully ready
        }

surveillance = SurveillanceService()

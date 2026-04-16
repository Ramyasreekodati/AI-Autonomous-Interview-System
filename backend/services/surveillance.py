import numpy as np
from sqlalchemy.orm import Session
import models
import datetime
import random

class SurveillanceService:
    def __init__(self):
        self._mp_holistic = None
        self._mp_face_mesh = None

    def _get_mp_components(self):
        if self._mp_face_mesh is None:
            try:
                import mediapipe as mp
                self.mp_face_mesh = mp.solutions.face_mesh
                self._face_mesh = self.mp_face_mesh.FaceMesh(
                    static_image_mode=False,
                    max_num_faces=5,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
            except Exception as e:
                print(f"MediaPipe load error: {e}")
                self._face_mesh = None
        return self._face_mesh

    def process_frame(self, frame_bytes, interview_id: int, db: Session):
        import cv2
        import datetime
        
        nparr = np.frombuffer(frame_bytes, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return {"error": "Invalid frame source"}

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_mesh = self._get_mp_components()
        
        alerts = []
        face_count = 0
        emotion = "Neutral"
        gaze_direction = "Center"

        if face_mesh:
            results = face_mesh.process(frame_rgb)
            if results.multi_face_landmarks:
                face_count = len(results.multi_face_landmarks)
                
                # Analyze primary face (index 0)
                landmarks = results.multi_face_landmarks[0].landmark
                
                # 4. IT Gaze Tracking (Simplified)
                # Looking at relative positions of eye landmarks
                left_eye = landmarks[468] # Center of left iris
                right_eye = landmarks[473] # Center of right iris
                
                # If iris center is far from eye boundary center -> looking away
                # Here we simulate with a basic bounding box check
                if left_eye.x < 0.4 or left_eye.x > 0.6:
                    gaze_direction = "Looking Away"
                    alerts.append({
                        "alert_type": "looking_away",
                        "timestamp": datetime.datetime.utcnow().isoformat(),
                        "severity": "low"
                    })

                # 3. Emotion Detection (Landmark-based heuristics)
                # Distance between eyebrows (stress), Lip curvature (confusion/confidence)
                brow_dist = abs(landmarks[107].y - landmarks[10].y) # Simplified stress proxy
                if brow_dist < 0.05:
                    emotion = "Stress"
                elif landmarks[13].y - landmarks[14].y > 0.02:
                    emotion = "Confidence (Speaking)"
                else:
                    emotion = "Neutral"

        # 1. Face Detection Check
        if face_count == 0:
            alerts.append({
                "alert_type": "face_not_detected",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "severity": "medium"
            })
        elif face_count > 1:
            alerts.append({
                "alert_type": "multiple_faces",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "severity": "high"
            })

        # 2. Object Detection (Phone simulation for now)
        # In a real setup, we use the object_detector service.
        # Here we simulate phone detection with 1% probability for demo stability
        if random.random() < 0.01:
            alerts.append({
                "alert_type": "phone_detected",
                "timestamp": datetime.datetime.utcnow().isoformat(),
                "severity": "high"
            })

        # Log alerts to database
        for alert_data in alerts:
            db_alert = models.Alert(
                interview_id=interview_id,
                alert_type=alert_data["alert_type"],
                severity=alert_data["severity"],
                timestamp=datetime.datetime.fromisoformat(alert_data["timestamp"])
            )
            db.add(db_alert)
        
        try:
            db.commit()
        except:
            db.rollback()

        return {
            "face_count": face_count,
            "emotion": emotion,
            "gaze": gaze_direction,
            "alerts": alerts
        }

surveillance = SurveillanceService()

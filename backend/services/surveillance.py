import cv2
import numpy as np
import datetime
import os

class SurveillanceService:
    def __init__(self):
        # 1. 👤 FACE / 👀 GAZE / 🧠 EMOTION (MediaPipe)
        self._face_mesh = None
        try:
            import mediapipe as mp
            self.mp_face_mesh = mp.solutions.face_mesh
            self._face_mesh = self.mp_face_mesh.FaceMesh(refine_landmarks=True)
        except: pass

        # 🎯 SMART ALERT PRIORITIZATION (Metadata)
        self.severity_map = {
            "no_face": "high",
            "multiple_faces": "high",
            "looking_away": "medium",
            "phone_detected": "high"
        }

    def process_frame_signals(self, image_data):
        if image_data is None: return [], "Normal", "Center"
        
        file_bytes = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        alerts = []
        emotion = "Confidence" # Default
        gaze = "Center"
        
        if self._face_mesh:
            results = self._face_mesh.process(rgb_img)
            if results.multi_face_landmarks:
                face_count = len(results.multi_face_landmarks)
                if face_count > 1:
                    alerts.append({"alert_type": "multiple_faces", "status": "FLAGGED", "severity": self.severity_map["multiple_faces"]})
                
                # 🧠 VOICE STRESS / EMOTION LANDMARKS
                landmarks = results.multi_face_landmarks[0].landmark
                
                # Eye Tracking (Iris Tracking)
                l_iris = landmarks[468]
                if l_iris.x < 0.46 or l_iris.x > 0.54:
                    gaze = "Looking Away"
                    alerts.append({"alert_type": "looking_away", "status": "DETECTED", "severity": self.severity_map["looking_away"]})
                
                # Emotion: Stress via Brow/Mouth ratio
                stress_signal = abs(landmarks[107].y - landmarks[9].y)
                if stress_signal < 0.04: emotion = "Stress (High Tension)"
                elif stress_signal > 0.08: emotion = "Surprise / Confusion"
            else:
                alerts.append({"alert_type": "no_face", "status": "ERROR", "severity": self.severity_map["no_face"]})

        return alerts, emotion, gaze

surveillance = SurveillanceService()

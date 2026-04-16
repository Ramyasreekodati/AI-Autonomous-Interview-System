import cv2
import numpy as np
import datetime

class SurveillanceService:
    def __init__(self):
        # Load the pre-trained Haar Cascade for face detection via OpenCV
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def detect_face_violation(self, image_data):
        """
        STRICT PHASE 3: Real OpenCV face counting logic.
        Detects 0 or >1 faces and returns structured alerts.
        """
        if image_data is None:
            return None, 0

        # Convert Streamlit UploadedFile (bytes) to OpenCV image
        try:
            file_bytes = np.asarray(bytearray(image_data.read()), dtype=np.uint8)
            img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Detect faces using Haar Cascade (Lightweight/Production Stable)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            count = len(faces)

            alert = None
            if count == 0:
                alert = {
                    "alert_type": "no_face", 
                    "timestamp": datetime.datetime.now().isoformat(), 
                    "severity": "high"
                }
            elif count > 1:
                alert = {
                    "alert_type": "multiple_faces", 
                    "timestamp": datetime.datetime.now().isoformat(), 
                    "severity": "high"
                }

            return alert, count
        except Exception as e:
            print(f"CV Error: {e}")
            return None, 0

surveillance = SurveillanceService()

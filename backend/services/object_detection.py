import cv2
import numpy as np
import os

class ObjectDetectionService:
    def __init__(self):
        # Using a simple MobileNet SSD for phone detection
        # We'll use the pre-trained weights from OpenCV's model zoo
        self.net = cv2.dnn.readNetFromCaffe(
            cv2.samples.findFile('deploy.prototxt'), 
            cv2.samples.findFile('mobilenet_iter_73000.caffemodel')
        )
        self.classes = {15: "person", 77: "cell phone"} # COCO class IDs (approx for SSD)

    def detect_phone(self, frame):
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 0.007843, (300, 300), 127.5)
        self.net.setInput(blob)
        detections = self.net.forward()
        
        detected = False
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > 0.5:
                idx = int(detections[0, 0, i, 1])
                if idx == 77:  # Cell phone
                    detected = True
                    break
        return detected

# Mock service if models aren't present
class MockObjectDetectionService:
    def detect_phone(self, frame):
        return False

# In a real setup, we would download the weights. 
# For this walkthrough, we'll provide the logic but use mock if files missing.
try:
    object_detector = ObjectDetectionService()
except:
    object_detector = MockObjectDetectionService()

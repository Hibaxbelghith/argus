import cv2
from deepface import DeepFace
import numpy as np

def run_live_emotion_detection():
    cap = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        try:
            # DeepFace expects RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = DeepFace.analyze(rgb_frame, actions=['emotion'], enforce_detection=False)
            # If multiple faces, results is a list
            if isinstance(results, list):
                for res in results:
                    x, y, w, h = res['region']['x'], res['region']['y'], res['region']['w'], res['region']['h']
                    emotion = res['dominant_emotion']
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                    cv2.putText(frame, emotion, (x, y-10), font, 1, (0, 255, 255), 2, cv2.LINE_AA)
            else:
                x, y, w, h = results['region']['x'], results['region']['y'], results['region']['w'], results['region']['h']
                emotion = results['dominant_emotion']
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 255), 2)
                cv2.putText(frame, emotion, (x, y-10), font, 1, (0, 255, 255), 2, cv2.LINE_AA)
        except Exception as e:
            pass  # Ignore detection errors for smooth video
        cv2.imshow('Live Emotion Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

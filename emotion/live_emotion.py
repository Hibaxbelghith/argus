import cv2
from deepface import DeepFace
import numpy as np

def run_live_emotion_detection():
    cap = None
    for cam_index in range(3):
        cap = cv2.VideoCapture(cam_index)
        if cap.isOpened():
            print(f"Using camera index {cam_index}")
            break
        cap.release()
    else:
        print("No camera found.")
        return
    
    # Set camera to maximum supported resolution
    resolutions = [
        (1920, 1080), # Full HD
        (1280, 720),  # HD
        (640, 480)    # VGA fallback
    ]
    for w, h in resolutions:
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
        actual_w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        actual_h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        if actual_w >= w * 0.9 and actual_h >= h * 0.9:  # Allow some tolerance
            print(f"Camera resolution set to {actual_w}x{actual_h}")
            break
    
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
        # Killswitch: exit if 'q' is pressed or window is closed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        # If window is closed, exit loop
        if cv2.getWindowProperty('Live Emotion Detection', cv2.WND_PROP_VISIBLE) < 1:
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_live_emotion_detection()

"""
Diagnostic Test Script with Real-Time Feedback.
Shows live skeletal landmarks and diagnosis (Closed Palm, Open Palm, 1 Finger, 2 Fingers).
Run this to test how accurately your hand is being detected!
"""

import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['GLOG_minloglevel'] = '3'

import cv2
from engine.gesture_detector import GestureDetector

def test_camera():
    print("[*] Initializing camera test...")
    detector = GestureDetector()
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("[-] Error: Could not access webcam. Please check if another app is using it.")
        return

    print("[+] Camera connected!")
    print("[*] Try closing your palm into a fist -> It will stay IDLE.")
    print("[*] Try opening your full hand -> It will stay IDLE.")
    print("[*] Show strictly 2 fingers (Index + Middle) -> It will show SCROLLING.")
    print("[*] Press 'q' on the preview window to exit.")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break

            should_scroll, preview = detector.process_frame(frame, draw_preview=True)

            cv2.putText(preview, "Press 'Q' to quit test", (20, 460), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)
            cv2.imshow("Gesture Scroller - Accuracy Test", preview)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    finally:
        cap.release()
        detector.close()
        cv2.destroyAllWindows()
        print("[+] Test finished.")

if __name__ == "__main__":
    test_camera()

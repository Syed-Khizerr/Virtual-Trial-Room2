"""
Live Camera View with Face Detection Debugging
This opens a window showing what your camera sees and draws rectangles where faces are detected
Press 'q' to quit, 's' to save a frame
"""

import cv2
import time

print("=" * 60)
print("Live Face Detection Debug Window")
print("=" * 60)
print("Controls:")
print("  'q' - Quit")
print("  's' - Save current frame")
print("  '1' - Try very lenient detection")
print("  '2' - Try normal detection")
print("  '3' - Try strict detection")
print("=" * 60)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("ERROR: Cannot access camera")
    exit(1)

time.sleep(0.5)  # Warm up

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

detection_mode = 1  # Start with lenient
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Try detection based on mode
    if detection_mode == 1:
        # Very lenient
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.05, minNeighbors=2, minSize=(20, 20)
        )
        mode_text = "Mode: VERY LENIENT (Press 2 for normal, 3 for strict)"
        color = (0, 255, 0)
    elif detection_mode == 2:
        # Normal
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
        )
        mode_text = "Mode: NORMAL (Press 1 for lenient, 3 for strict)"
        color = (0, 255, 255)
    else:
        # Strict
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=5, minSize=(50, 50)
        )
        mode_text = "Mode: STRICT (Press 1 for lenient, 2 for normal)"
        color = (0, 0, 255)
    
    # Draw face rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        cv2.putText(frame, f"Face {w}x{h}", (x, y-10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
    
    # Display info
    cv2.putText(frame, mode_text, (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, f"Faces detected: {len(faces)}", (10, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    cv2.putText(frame, "Press 'q' to quit, 's' to save", (10, frame.shape[0] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('Camera - Face Detection Debug', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        filename = f'debug_saved_{saved_count}.jpg'
        cv2.imwrite(filename, frame)
        saved_count += 1
        print(f"Saved: {filename}")
    elif key == ord('1'):
        detection_mode = 1
        print("Switched to VERY LENIENT mode")
    elif key == ord('2'):
        detection_mode = 2
        print("Switched to NORMAL mode")
    elif key == ord('3'):
        detection_mode = 3
        print("Switched to STRICT mode")

cap.release()
cv2.destroyAllWindows()
print("\nDebug session ended.")

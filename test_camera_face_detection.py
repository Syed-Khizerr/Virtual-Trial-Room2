"""
Test script to verify camera and face detection are working
Run this to debug face detection issues before testing the main Flask app
"""

import cv2
import time

print("=" * 60)
print("Camera and Face Detection Test")
print("=" * 60)

# Test 1: Check if camera is accessible
print("\n[1/4] Testing camera access...")
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Cannot access camera")
    print("   - Check if camera is connected")
    print("   - Close other apps using the camera")
    print("   - Check camera permissions")
    exit(1)
else:
    print("✅ Camera accessed successfully")

# Test 2: Read a frame
print("\n[2/4] Testing frame capture...")
time.sleep(0.5)  # Give camera time to warm up
ret, frame = cap.read()
if not ret or frame is None:
    print("❌ ERROR: Cannot read from camera")
    cap.release()
    exit(1)
else:
    print(f"✅ Frame captured: {frame.shape[1]}x{frame.shape[0]} pixels")

# Test 3: Load face detection model
print("\n[3/4] Testing face detection model...")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    print("❌ ERROR: Could not load face detection model")
    cap.release()
    exit(1)
else:
    print("✅ Face detection model loaded")

# Test 4: Try to detect faces
print("\n[4/4] Testing face detection (will try for 10 seconds)...")
print("   📷 Position your face in front of the camera...")

face_detected = False
start_time = time.time()
attempts = 0

while time.time() - start_time < 10:
    attempts += 1
    ret, frame = cap.read()
    if not ret:
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Try different detection parameters
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=3,
        minSize=(30, 30),
        flags=cv2.CASCADE_SCALE_IMAGE
    )
    
    if len(faces) > 0:
        face_detected = True
        print(f"✅ Face detected! Found {len(faces)} face(s)")
        for i, (x, y, w, h) in enumerate(faces):
            print(f"   Face {i+1}: Position=({x},{y}), Size={w}x{h}")
        break
    
    time.sleep(0.1)

if not face_detected:
    print(f"❌ No face detected after {attempts} attempts")
    print("\n   Troubleshooting tips:")
    print("   - Ensure good lighting")
    print("   - Face the camera directly")
    print("   - Remove glasses/hat if wearing")
    print("   - Move closer or farther from camera")
    print("   - Try different angles")
else:
    print(f"\n🎉 All tests passed! Face detected after {attempts} attempts")
    print("   Your camera and face detection are working correctly.")

cap.release()
print("\n" + "=" * 60)
print("Test complete!")
print("=" * 60)

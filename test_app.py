"""
Test the virtual try-on WITHOUT face detection
This will place clothes at fixed positions to verify the overlay logic works
"""

from flask import Flask, render_template, request, send_file
from flask_cors import CORS
import cv2
import os

app = Flask(__name__)
CORS(app)

# Ensure output directory exists
os.makedirs('static/output', exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/shirt.html')
def plot():
    return render_template('shirt.html')

@app.route('/pant.html')
def ploty():
    return render_template('pant.html')

@app.route('/test-overlay', methods=['GET', 'POST'])
def test_overlay():
    """Test version that doesn't require face detection"""
    try:
        shirtno = int(request.args.get("shirt", 1))
        pantno = int(request.args.get("pant", 1))
    except ValueError:
        return "Invalid parameters", 400
    
    # Get script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Open camera
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        return "Error: Cannot access camera", 500
    
    # Read a frame
    import time
    time.sleep(0.5)
    ret, img = cap.read()
    cap.release()
    
    if not ret or img is None:
        return "Error: Cannot read from camera", 500
    
    # Load shirt and pant
    shirt_images = [
        os.path.join(script_dir, "shirt1.png"),
        os.path.join(script_dir, 'shirt2.png'),
        os.path.join(script_dir, 'shirt51.jpg'),
        os.path.join(script_dir, 'shirt6.png')
    ]
    
    pant_images = [
        os.path.join(script_dir, "pant7.jpg"),
        os.path.join(script_dir, 'pant21.png')
    ]
    
    imgshirt = cv2.imread(shirt_images[shirtno-1], 1)
    imgpant = cv2.imread(pant_images[pantno-1], 1)
    
    if imgshirt is None or imgpant is None:
        return "Error loading images", 404
    
    # Use fixed positions (center of frame)
    height, width = img.shape[:2]
    
    # Simulate face at center
    face_w = width // 4
    face_h = height // 4
    face_x = width // 2 - face_w // 2
    face_y = height // 6
    
    # Draw simulated face rectangle
    cv2.rectangle(img, (face_x, face_y), (face_x + face_w, face_y + face_h), (0, 255, 0), 2)
    cv2.putText(img, "Simulated Face Area", (face_x, face_y - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Process shirt overlay
    shirt_w = int(face_w * 3)
    shirt_h = int(shirt_w * imgshirt.shape[0] / imgshirt.shape[1])
    shirt_x = face_x - face_w
    shirt_y = face_y + face_h
    
    # Ensure bounds
    shirt_x = max(0, shirt_x)
    shirt_y = max(0, shirt_y)
    if shirt_y + shirt_h > height:
        shirt_h = height - shirt_y
    if shirt_x + shirt_w > width:
        shirt_w = width - shirt_x
    
    if shirt_w > 0 and shirt_h > 0:
        shirt_resized = cv2.resize(imgshirt, (shirt_w, shirt_h))
        # Simple alpha blend
        alpha = 0.7
        roi = img[shirt_y:shirt_y+shirt_h, shirt_x:shirt_x+shirt_w]
        if roi.shape[:2] == shirt_resized.shape[:2]:
            blended = cv2.addWeighted(roi, 1-alpha, shirt_resized, alpha, 0)
            img[shirt_y:shirt_y+shirt_h, shirt_x:shirt_x+shirt_w] = blended
    
    # Process pant overlay
    pant_w = int(face_w * 2)
    pant_h = int(pant_w * imgpant.shape[0] / imgpant.shape[1])
    pant_x = face_x - face_w // 2
    pant_y = shirt_y + shirt_h
    
    # Ensure bounds
    pant_x = max(0, pant_x)
    pant_y = max(0, pant_y)
    if pant_y + pant_h > height:
        pant_h = height - pant_y
    if pant_x + pant_w > width:
        pant_w = width - pant_x
    
    if pant_w > 0 and pant_h > 0:
        pant_resized = cv2.resize(imgpant, (pant_w, pant_h))
        alpha = 0.7
        roi = img[pant_y:pant_y+pant_h, pant_x:pant_x+pant_w]
        if roi.shape[:2] == pant_resized.shape[:2]:
            blended = cv2.addWeighted(roi, 1-alpha, pant_resized, alpha, 0)
            img[pant_y:pant_y+pant_h, pant_x:pant_x+pant_w] = blended
    
    # Save output
    output_filename = f'test_output_{shirtno}_{pantno}.jpg'
    output_path = os.path.join('static', 'output', output_filename)
    cv2.imwrite(output_path, img)
    
    return send_file(output_path, mimetype='image/jpeg')

if __name__ == '__main__':
    print("=" * 60)
    print("TEST MODE - No Face Detection Required")
    print("=" * 60)
    print("\nAccess the test overlay at:")
    print("  http://localhost:5001/test-overlay?shirt=1&pant=1")
    print("\nChange shirt (1-4) and pant (1-2) in the URL")
    print("=" * 60)
    app.run(host='0.0.0.0', debug=True, port=5001)

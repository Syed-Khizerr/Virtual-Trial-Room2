from flask import Flask, render_template, request
from flask_cors import CORS
import numpy as np
import cv2                              # Library for image processing
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
@app.route('/predict', methods=['GET','POST'])
def predict():
    try:
        shirtno = int(request.form["shirt"])
        pantno = int(request.form["pant"])
        
        # Input validation
        if not (1 <= shirtno <= 4):
            return "Invalid shirt number. Please select 1-4.", 400
        if not (1 <= pantno <= 2):
            return "Invalid pant number. Please select 1-2.", 400
    except (KeyError, ValueError):
        return "Missing or invalid form data", 400

    cv2.waitKey(1)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        return "Error: Cannot access camera", 500
    
    ih = shirtno
    i = pantno
    
    output_image = None
    max_attempts = 100  # Limit loop iterations
    attempt = 0
    
    # Get the directory where this script is located (for absolute paths)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    while attempt < max_attempts:
        attempt += 1
        imgarr = [
            os.path.join(script_dir, "shirt1.png"),
            os.path.join(script_dir, "shirt2.png"),
            os.path.join(script_dir, "shirt51.jpg"),
            os.path.join(script_dir, "shirt6.png")
        ]

        #ih=input("Enter the shirt number you want to try")
        imgshirt = cv2.imread(imgarr[ih-1], 1)  # original img in bgr
        
        if imgshirt is None:
            cap.release()
            return f"Error: Shirt image '{imgarr[ih-1]}' not found", 404
        
        if ih == 3:
            shirtgray = cv2.cvtColor(imgshirt, cv2.COLOR_BGR2GRAY)  # grayscale conversion
            ret, orig_masks_inv = cv2.threshold(shirtgray, 200, 255, cv2.THRESH_BINARY)
            orig_masks = cv2.bitwise_not(orig_masks_inv)
        else:
            shirtgray = cv2.cvtColor(imgshirt, cv2.COLOR_BGR2GRAY)  # grayscale conversion
            ret, orig_masks = cv2.threshold(shirtgray, 0, 255, cv2.THRESH_BINARY)
            orig_masks_inv = cv2.bitwise_not(orig_masks)
        
        origshirtHeight, origshirtWidth = imgshirt.shape[:2]
        
        if origshirtWidth == 0 or origshirtHeight == 0:
            cap.release()
            return "Error: Invalid shirt image dimensions", 400
        
        imgarr = [
            os.path.join(script_dir, "pant7.jpg"),
            os.path.join(script_dir, "pant21.png")
        ]
        #i=input("Enter the pant number you want to try")
        imgpant = cv2.imread(imgarr[i-1], 1)
        
        if imgpant is None:
            cap.release()
            return f"Error: Pant image '{imgarr[i-1]}' not found", 404
        
        imgpant = imgpant[:, :, 0:3]  # original img in bgr
        pantgray = cv2.cvtColor(imgpant, cv2.COLOR_BGR2GRAY)  # grayscale conversion
        
        if i == 1:
            ret, orig_mask = cv2.threshold(pantgray, 100, 255, cv2.THRESH_BINARY)
            orig_mask_inv = cv2.bitwise_not(orig_mask)
        else:
            ret, orig_mask = cv2.threshold(pantgray, 50, 255, cv2.THRESH_BINARY)
            orig_mask_inv = cv2.bitwise_not(orig_mask)
        
        origpantHeight, origpantWidth = imgpant.shape[:2]
        
        if origpantWidth == 0 or origpantHeight == 0:
            cap.release()
            return "Error: Invalid pant image dimensions", 400
        
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        ret, img = cap.read()
        
        if not ret or img is None:
            cap.release()
            return "Error: Cannot read from camera", 500
       
        height = img.shape[0]
        width = img.shape[1]
        resizewidth = int(width * 3 / 2)
        resizeheight = int(height * 3 / 2)
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
            cv2.rectangle(img, (100, 200), (312, 559), (255, 255, 255), 2)
            pantWidth = 3 * w  # approx wrt face width
            pantHeight = pantWidth * origpantHeight / origpantWidth  # preserving aspect ratio of original image

            # Center the pant..just random calculations..
            if i == 1:
                x1 = x - w
                x2 = x1 + 3*w
                y1 = y + 5*h
                y2 = y + h*10
            elif i == 2:
                x1 = x - w/2
                x2 = x1 + 2*w
                y1 = y + 4*h
                y2 = y + h*9
            else:
                x1 = x - w/2
                x2 = x1 + 5*w/2
                y1 = y + 5*h
                y2 = y + h*14
            # Check for clipping(whether x1 is coming out to be negative or not..)

            if x1 < 0:
                x1 = 0  # top left boundary
            if x2 > img.shape[1]:
                x2 = img.shape[1]  # bottom right boundary
            if y2 > img.shape[0]:
                y2 = img.shape[0]  # bottom boundary
            if y1 > img.shape[0]:
                y1 = img.shape[0]  # bottom boundary
            if y1 == y2:
                y1 = 0
            temp = 0
            if y1 > y2:
                temp = y1
                y1 = y2
                y2 = temp
            
            # Re-calculate the width and height of the pant image(to resize the image when it wud be pasted)
            pantWidth = int(abs(x2 - x1))
            pantHeight = int(abs(y2 - y1))
            
            # Skip if dimensions are invalid
            if pantWidth == 0 or pantHeight == 0:
                continue
            
            x1 = int(x1)
            x2 = int(x2)
            y1 = int(y1)
            y2 = int(y2)
            
            # Re-size the original image and the masks to the pant sizes
            pant = cv2.resize(imgpant, (pantWidth, pantHeight), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(orig_mask, (pantWidth, pantHeight), interpolation=cv2.INTER_AREA)
            mask_inv = cv2.resize(orig_mask_inv, (pantWidth, pantHeight), interpolation=cv2.INTER_AREA)
            
            # take ROI for pant from background equal to size of pant image
            roi = img[y1:y2, x1:x2]
            # roi_bg contains the original image only where the pant is not
            roi_bg = cv2.bitwise_and(roi, roi, mask=mask_inv)
            # roi_fg contains the image of the pant only where the pant is
            roi_fg = cv2.bitwise_and(pant, pant, mask=mask)
            # join the roi_bg and roi_fg
            dst = cv2.add(roi_bg, roi_fg)
            # place the joined image, saved to dst back over the original image
            
            # Bounds checking for blur regions
            blur_y_end = min(y + h, img.shape[0], resizeheight)
            blur_x_end = min(x + w, img.shape[1], resizewidth)
            resizewidth = min(resizewidth, img.shape[1])
            resizeheight = min(resizeheight, img.shape[0])
            
            # Apply gaussian blur to background regions
            blurvalue = 5
            if y > 0 and resizewidth > 0:
                top = img[0:y, 0:resizewidth]
                if top.size > 0:
                    top = cv2.GaussianBlur(top, (blurvalue, blurvalue), 0)
                    img[0:y, 0:resizewidth] = top
            
            if blur_y_end < resizeheight and resizewidth > 0:
                bottom = img[blur_y_end:resizeheight, 0:resizewidth]
                if bottom.size > 0:
                    bottom = cv2.GaussianBlur(bottom, (blurvalue, blurvalue), 0)
                    img[blur_y_end:resizeheight, 0:resizewidth] = bottom
            
            if x > 0:
                midleft = img[y:blur_y_end, 0:x]
                if midleft.size > 0:
                    midleft = cv2.GaussianBlur(midleft, (blurvalue, blurvalue), 0)
                    img[y:blur_y_end, 0:x] = midleft
            
            if blur_x_end < resizewidth:
                midright = img[y:blur_y_end, blur_x_end:resizewidth]
                if midright.size > 0:
                    midright = cv2.GaussianBlur(midright, (blurvalue, blurvalue), 0)
                    img[y:blur_y_end, blur_x_end:resizewidth] = midright
            
            img[y1:y2, x1:x2] = dst

            # SHIRT OVERLAY
            shirtWidth = 3 * w  # approx wrt face width
            shirtHeight = shirtWidth * origshirtHeight / origshirtWidth  # preserving aspect ratio of original image
            # Center the shirt..just random calculations..
            x1s = x - w
            x2s = x1s + 3*w
            y1s = y + h
            y2s = y1s + h*4
            # Check for clipping(whether x1 is coming out to be negative or not..)

            if x1s < 0:
                x1s = 0
            if x2s > img.shape[1]:
                x2s = img.shape[1]
            if y2s > img.shape[0]:
                y2s = img.shape[0]
            temp = 0
            if y1s > y2s:
                temp = y1s
                y1s = y2s
                y2s = temp
            
            # Re-calculate the width and height of the shirt image(to resize the image when it wud be pasted)
            shirtWidth = int(abs(x2s - x1s))
            shirtHeight = int(abs(y2s - y1s))
            
            # Skip if dimensions are invalid
            if shirtWidth == 0 or shirtHeight == 0:
                continue
            
            y1s = int(y1s)
            y2s = int(y2s)
            x1s = int(x1s)
            x2s = int(x2s)
            
            # Re-size the original image and the masks to the shirt sizes
            shirt = cv2.resize(imgshirt, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)
            mask = cv2.resize(orig_masks, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)
            masks_inv = cv2.resize(orig_masks_inv, (shirtWidth, shirtHeight), interpolation=cv2.INTER_AREA)
            # take ROI for shirt from background equal to size of shirt image
            rois = img[y1s:y2s, x1s:x2s]
            # roi_bg contains the original image only where the shirt is not
            roi_bgs = cv2.bitwise_and(rois, rois, mask=masks_inv)
            # roi_fg contains the image of the shirt only where the shirt is
            roi_fgs = cv2.bitwise_and(shirt, shirt, mask=mask)
            # join the roi_bg and roi_fg
            dsts = cv2.add(roi_bgs, roi_fgs)
            img[y1s:y2s, x1s:x2s] = dsts  # place the joined image, saved to dst back over the original image
            
            # Store the output image and break
            output_image = img.copy()
            break
        
        # If we've processed or no face detected, check if we should continue
        if output_image is not None:
            break

    cap.release()  # Destroys the cap object

    # Check if we successfully created an output image
    if output_image is None:
        return "Error: No face detected. Please ensure your face is visible to the camera.", 400
    
    # Save the output image
    output_filename = f'output_{shirtno}_{pantno}.jpg'
    output_path = os.path.join('static', 'output', output_filename)
    cv2.imwrite(output_path, output_image)
    
    # Return the result page with the output image
    return render_template('index.html', output_image=output_filename)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True,port=5000)

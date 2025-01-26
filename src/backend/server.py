from flask import Flask, request, jsonify
import os
import base64
from io import BytesIO
import PIL
from PIL import Image
from flask_cors import CORS  # Add this import
import numpy as np
import cv2

app = Flask(__name__)

# enable CORS for all routes
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        file = request.files['file']
        
        # If no file is selected
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
        
        # Open the image file
        img = Image.open(file.stream)
        np_img = np.array(img)
        
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        print("HERREEEEE")
        
        # Encode image to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        json_data = jsonify({"image": img_base64})
        print("BASE64:", type(img_base64))
        return json_data, 200
    except Exception as e:
        return jsonify({"message": f"Error uploading image: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)
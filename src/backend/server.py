from flask import Flask, request, jsonify
import os
import base64
from io import BytesIO
import PIL
from PIL import Image
from flask_cors import CORS  # Add this import
import numpy as np
import cv2
from main import getCueTips
from physics.simulatePaths import main

app = Flask(__name__)

# enable CORS for all routes
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

sim_env_data = None # Holds uploaded

@app.route('/upload', methods=['POST'])
def upload_image():
    global sim_env_data # So i can use it for sim
    
    try:
        file = request.files['file']
        # If no file is selected
        if file.filename == '':
            return jsonify({"message": "No selected file"}), 400
        
        # Open the image file
        img = Image.open(file.stream)
        np_img = np.array(img)

        # test img 
        img = cv2.imread("/Users/jacobleader/Desktop/Code/CueTips/data/pool_table_overhead.png")
        table_graphic, _, sim_env_data = getCueTips(img, run_sim=False) 
        img_rgb = cv2.cvtColor(table_graphic, cv2.COLOR_BGR2RGB)

        pil_img = Image.fromarray(img_rgb)
        # Save the image into a BytesIO object
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        buffered.seek(0)

        
        # Encode image to base64
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        json_data = jsonify({"image": img_base64})

        return json_data, 200
    except Exception as e:
        return jsonify({"message": f"Error uploading image: {str(e)}"}), 500

@app.route('/sim', methods=['POST'])
def sim_angle():
    try:
        request_data = request.get_json()
        cue_angle = request_data.get('cue_angle')

        pool_balls, pockets, edges, avg_radius = sim_env_data
        tempfile_svg_name = main(pool_balls, pockets, cue_ball=None, wall_cords=edges, ball_radius=avg_radius, cue_angle=cue_angle, show_simulation=False)
        
        with open(tempfile_svg_name, 'r') as f:
            svg_content = f.read()
 
        # Encode image to base64
        json_data = jsonify({"svg": svg_content})

        return json_data, 200
    except Exception as e:
        return jsonify({"message": f"Error uploading svg: {str(e)}"}), 500
    
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)
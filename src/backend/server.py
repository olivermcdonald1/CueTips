from flask import Flask, request, jsonify
import os
import base64
from io import BytesIO
from PIL import Image
from flask_cors import CORS
import numpy as np
import cv2
from main import getCueTips
from physics.simulatePaths import main
import pygame

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

sim_env_data = None  # Global state for simulation (not ideal for production)

@app.route('/upload', methods=['POST'])
def upload_image():
    global sim_env_data
    try:
        file = request.files.get('file')
        if not file or file.filename == '':
            return jsonify({"message": "No selected file"}), 400

        img = Image.open(file.stream)
        img = np.array(img)

        # Test image - make sure this file exists
        test_img_path = "/Users/jacobleader/Desktop/Code/CueTips/data/pool_table_overhead.png"
        if not os.path.exists(test_img_path):
            return jsonify({"message": f"Test image not found at {test_img_path}"}), 500

        img = cv2.imread(test_img_path)
        table_graphic, _, cue_ball_cords, sim_env_data = getCueTips(img, run_sim=False)

        img_rgb = cv2.cvtColor(table_graphic, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        buffered = BytesIO()
        pil_img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return jsonify({"image": img_base64}), 200
    except Exception as e:
        return jsonify({"message": f"Error uploading image: {str(e)}"}), 500


@app.route('/sim', methods=['POST'])
def sim_angle():
    global sim_env_data
    try:
        if not sim_env_data:
            return jsonify({"message": "Simulation environment data not initialized"}), 400

        request_data = request.get_json()
        cue_angle = request_data.get('cue_angle')
        if cue_angle is None:
            return jsonify({"message": "Missing cue_angle in request"}), 400

        pool_balls, edges, avg_radius = sim_env_data
        tempfile_svg_name, cue_ball_pos_start = main(pool_balls, wall_cords=edges, ball_radius=avg_radius, cue_angle=cue_angle, show_simulation=False)
        with open(tempfile_svg_name, 'r') as f:
            svg_content = f.read()
        print(type(svg_content))
        os.remove(tempfile_svg_name)  # Clean up temporary file
        
        return jsonify({"svg": svg_content}), 200
    except Exception as e:
        return jsonify({"message": f"Error running simulation: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=4000)

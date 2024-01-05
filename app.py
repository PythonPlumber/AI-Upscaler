from flask import Flask, render_template, request, send_from_directory, jsonify
from PIL import Image
import cv2
import os
import threading
import time

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'ico', 'jfif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upscale_image(input_path, output_path, scale_factor):
    image = cv2.imread(input_path)
    upscaled_image = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(output_path, upscaled_image)

def create_directories():
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

create_directories()

def process_upscaling(input_path, output_path_base, scales, response_queue):
    for scale in scales:
        output_path = f"{output_path_base}_{scale}x.png"
        upscale_image(input_path, output_path, scale)

    response_queue.put(True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return render_template('index.html', error='No file part')

    file = request.files['file']

    if file.filename == '':
        return render_template('index.html', error='No selected file')

    if file and allowed_file(file.filename):
        create_directories()  # Ensure directories exist
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        output_path_base = os.path.join(app.config['OUTPUT_FOLDER'], file.filename.split('.')[0])
        file.save(input_path)

        scales = [2, 4, 6, 8, 10]
        response_queue = []

        # Start a thread for upscaling
        thread = threading.Thread(target=process_upscaling, args=(input_path, output_path_base, scales, response_queue))
        thread.start()

        return render_template('processing.html', input_path=input_path, scales=scales)

    return render_template('index.html', error='Invalid file format')

@app.route('/status/<task_id>')
def task_status(task_id):
    response_queue = app.config['response_queue']

    if task_id in response_queue:
        return jsonify({'status': 'completed'})
    else:
        return jsonify({'status': 'processing'})

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.config['response_queue'] = []
    app.run(debug=True)

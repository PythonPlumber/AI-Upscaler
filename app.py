from flask import Flask, render_template, request, send_from_directory
from PIL import Image
import cv2
import os

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upscale_image(input_path, output_path, scale_factor):
    image = cv2.imread(input_path)
    upscaled_image = cv2.resize(image, (0, 0), fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_LINEAR)
    cv2.imwrite(output_path, upscaled_image)

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
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        output_path_base = os.path.join(app.config['OUTPUT_FOLDER'], file.filename.split('.')[0])
        file.save(input_path)

        scales = [2, 4, 6, 8, 10]

        for scale in scales:
            output_path = f"{output_path_base}_{scale}x.png"
            upscale_image(input_path, output_path, scale)

        return render_template('result.html', input_path=input_path, scales=scales)

    return render_template('index.html', error='Invalid file format')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/output/<filename>')
def output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
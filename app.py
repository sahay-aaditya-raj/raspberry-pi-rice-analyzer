from flask import Flask, render_template, Response, request, redirect, url_for, jsonify
import os
import time
from werkzeug.utils import secure_filename
from camera import Camera  # Using RPi Camera Module
import cv2
from process_image import process_image  # Our custom image processing function

app = Flask(__name__)

# Folders setup
# Upload Doesnt have signigicane so can remove or keep
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

CAPTURE_FOLDER = 'static/captured'
os.makedirs(CAPTURE_FOLDER, exist_ok=True)

PROCESSED_FOLDER = os.path.join(app.root_path, 'static', 'processed')
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CAPTURE_FOLDER'] = CAPTURE_FOLDER
app.config['PROCESSED_FOLDER'] = PROCESSED_FOLDER

camera = Camera()

MAX_IMAGES = 50

def cleanup_old_images(directory, max_files=10):
    """Deletes the oldest image if the directory contains more than `max_files` images."""
    files = sorted(
        (os.path.join(directory, f) for f in os.listdir(directory) if f.endswith('.jpg')),
        key=os.path.getctime  # Sort by creation time (oldest first)
    )
    while len(files) > max_files:
        os.remove(files.pop(0))  # Remove oldest file

def manage_captured_images():
    """Ensures that only the last 10 captured images are stored."""
    images = sorted(os.listdir(CAPTURE_FOLDER), key=lambda x: os.path.getctime(os.path.join(CAPTURE_FOLDER, x)))
    while len(images) > MAX_IMAGES:
        os.remove(os.path.join(CAPTURE_FOLDER, images.pop(0)))

def gen(camera):
    """Generates frames for live video feed."""
    while True:
        frame = camera.get_frame()
        if not frame:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Routes
@app.route('/video_feed')
def video_feed():
    """Live streaming route."""
    return Response(gen(camera), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/capture', methods=['POST'])
def capture():
    """Captures an image from the camera and saves it."""
    frame = camera.get_frame()
    if frame:
        timestamp = int(time.time())  # Unique filename based on timestamp
        filename = f"captured_{timestamp}.jpg"
        filepath = os.path.join(app.config['CAPTURE_FOLDER'], filename)
        with open(filepath, "wb") as f:
            f.write(frame)
        manage_captured_images()  # Keep only the last 10 images
        return jsonify({"image_url": url_for('static', filename=f'captured/{filename}')})
    return jsonify({"error": "Capture failed"}), 500

@app.route('/process_image', methods=['POST'])
def process_image_route():
    """
    Processes an image to detect and analyze rice grains, stones, and husks.
    Returns detailed analysis results including different types of grains.
    """
    data = request.get_json()
    image_path = data.get("image_path")

    if not image_path:
        return jsonify({"error": "Invalid request"}), 400

    # Build full path to the image (remove any leading '/' if present)
    image_full_path = os.path.join(app.root_path, image_path.lstrip('/'))
    
    image = cv2.imread(image_full_path)
    if image is None:
        return jsonify({"error": "Image not found"}), 404

    # Process image with updated process_image function
    try:
        processed_result = process_image(image)
        
        # Unpack results from the tuple (updated to match new return values)
        final_image = processed_result[0]
        full_grain_count = processed_result[1]
        chalky_count = processed_result[2]
        black_count = processed_result[3]
        yellow_count = processed_result[4]
        brown_count = processed_result[5]
        broken_percentages = processed_result[6]
        broken_grain_count = processed_result[7]
        stone_count = processed_result[8]
        husk_count = processed_result[9]

        # Calculate total count
        total_objects = full_grain_count + chalky_count + black_count + yellow_count + brown_count + broken_grain_count + stone_count + husk_count

        # Save processed image with a timestamp-based filename
        processed_filename = f"processed_{int(time.time())}.jpg"
        processed_filepath = os.path.join(PROCESSED_FOLDER, processed_filename)
        cv2.imwrite(processed_filepath, final_image)

        # Cleanup old processed images (keep only 50)
        cleanup_old_images(PROCESSED_FOLDER, max_files=MAX_IMAGES)

        return jsonify({
            "processed_image_url": url_for('static', filename=f'processed/{processed_filename}'),
            "total_objects": total_objects,
            "full_grain_count": full_grain_count,
            "chalky_count": chalky_count,
            "black_count": black_count,
            "yellow_count": yellow_count,
            "brown_count": brown_count,
            "broken_percentages": broken_percentages,
            "broken_grain_count": broken_grain_count,
            "stone_count": stone_count,
            "husk_count": husk_count
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    """Handles file upload and renders the main page."""
    uploaded_image = None
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error='No file uploaded')
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error='No selected file')
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        uploaded_image = filepath
    return render_template('index.html', uploaded_image=uploaded_image)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5001, use_reloader=False)
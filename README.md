# Raspberry Pi Rice & Dal Analyzer

A Flask-based web application for analyzing rice and dal grain quality using image processing and computer vision. Designed for use on a Raspberry Pi with a PiCamera, this project provides a user-friendly interface for capturing images, analyzing grain quality, and managing WiFi connections.

## Features

- **Live Camera Feed & Capture**: Stream video from the PiCamera and capture images for analysis.
- **Rice & Dal Analysis**: Detects and counts full, broken, chalky, black, yellow, brown, stone, and husk grains in rice; and full, broken, and black dal grains using OpenCV-based image processing.
- **Batch Results & Local Storage**: Saves analysis results locally as JSON files, with device ID and timestamp.
- **MongoDB Sync**: Periodically syncs local results to a remote MongoDB database (see `mongo_sync_standalone.py` and `mongodb_sync.py`).
- **WiFi Management**: Scan, connect, disconnect, and view WiFi status via a web UI (see `/wifi` route).
- **Modern UI**: Responsive Bootstrap-based interface with custom styles and a virtual keyboard for easy use on touchscreens.
- **System Controls**: Shutdown and restart the Raspberry Pi from the web interface.

## Project Structure

```
app.py                  # Main Flask app with all routes
camera.py               # PiCamera2 interface for image capture
process_image.py        # Rice grain analysis logic
procress_dal.py         # Dal grain analysis logic
wifi_manager.py         # WiFi scan/connect/disconnect/status logic
config.py               # Configuration (MongoDB, local storage, etc.)
mongodb_models.py       # MongoDB document schemas
mongodb_sync.py         # MongoDB sync logic (used by app)
mongo_sync_standalone.py# Standalone MongoDB sync script
static/                 # Static files (JS, CSS, images)
  ├── bootstrap.css, bootstrap.bundle.js
  ├── script.js         # Main UI logic
  ├── js/wifi.js        # WiFi page JS
  ├── css/wifi.css      # WiFi page CSS
  ├── styles.css        # Main UI CSS
  ├── captured/         # Captured images
  ├── processed/        # Processed images
  └── uploads/          # Uploaded images
templates/              # Jinja2 HTML templates
  ├── index.html        # Main UI
  └── wifi.html         # WiFi management UI
```

## Setup & Usage

### Prerequisites
- Raspberry Pi (tested on Pi 4)
- PiCamera2 module
- Python 3.7+
- MongoDB Atlas account (for cloud sync)

### Installation
1. **Clone the repository:**
   ```sh
   git clone <repo-url>
   cd raspberry-pi-rice-analyzer
   ```
2. **Install dependencies:**
   ```sh
   pip install flask opencv-python picamera2 pymongo pillow
   ```
3. **Configure MongoDB:**
   - Edit `config.py` with your MongoDB URI and database/collection names.

4. **Run the Flask app:**
   ```sh
   python app.py
   ```
   - Access the web UI at `http://<raspberry-pi-ip>:5000/`

5. **(Optional) Start MongoDB Sync:**
   - In a separate terminal, run:
     ```sh
     python mongo_sync_standalone.py
     ```

### Usage
- **Capture**: Click 'Capture' to take a photo from the camera.
- **Analyze-Rice / Analyze-Dal**: Analyze the captured image for rice or dal quality.
- **Save**: Save the results locally (and sync to MongoDB if configured).
- **WiFi**: Go to the 'Utils' page to manage WiFi connections.
- **Shutdown/Restart**: Use the buttons on the WiFi page to safely power off or reboot the Pi.

## Customization
- **Image Processing**: Tweak thresholds and logic in `process_image.py` and `procress_dal.py` for your specific grain types.
- **UI**: Modify `templates/index.html`, `static/styles.css`, and `static/script.js` for custom branding or features.

## License
MIT License

## Acknowledgements
- [Flask](https://flask.palletsprojects.com/)
- [OpenCV](https://opencv.org/)
- [PiCamera2](https://github.com/raspberrypi/picamera2)
- [Bootstrap](https://getbootstrap.com/)

---
For questions or contributions, please open an issue or pull request.

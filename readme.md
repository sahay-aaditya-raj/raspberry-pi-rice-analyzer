# Raspberry Pi Image Processing System

A image processing application for rice quality analysis using Raspberry Pi Camera Module. This project detects and counts rice grains, stones, and husk in real-time captured images.

## Features

- Live video stream from Raspberry Pi Camera
- Image capture and storage
- Automated detection and counting of:
  - Full rice grains
  - Broken rice grains
  - Stones
  - Husk
- Visual overlay of detected objects with color-coded masks
- REST API for image processing
- Web interface for capturing and analyzing images

## Hardware Requirements

- Raspberry Pi (4 recommended)
- Raspberry Pi Camera Module 3 (Sony IMX708 12.3MP HDR, built-in phase-detect autofocus actuator)
- MicroSD card with Raspberry Pi OS
- Power supply and peripherals

## Software Dependencies

- Python 3.10+
- Flask
- OpenCV (cv2)
- Picamera2
- NumPy
- PIL (Python Imaging Library)
- Matplotlib (for testing)

## Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/raspberry-pi-image-processing.git
   cd raspberry-pi-image-processing
   ```

2. **Install Python Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Enable Camera Interface**
   - Run `sudo raspi-config`
   - Navigate to **Interface Options** > **Camera** > **Enable**

4. **Run the Application**
   ```bash
   python app.py
   ```

5. **Access the Web Interface**
   - Open a web browser and navigate to `http://<raspberry-pi-ip>:5001`
   - Default port is 5001

## Usage

1. **Live Video Feed**
   - View the live camera feed on the main page

2. **Capture Image**
   - Click the "Capture" button to take a photo
   - The captured image will be displayed below the video feed

3. **Analyze Image**
   - Click "Analyze" to process the captured image
   - Results will be displayed with color-coded overlays:
     - Green: Full rice grains
     - Blue: Broken rice grains
     - Yellow: Stones
     - Pink: Husk

4. **Retake Image**
   - Click "Retake" to capture a new image

## Project Structure

```
raspberry-pi-image-processing/
├── app.py                  # Main Flask application
├── camera.py               # Camera module implementation
├── process_image.py        # Image processing functions
├── static/                 # Static files
│   ├── uploads/            # User uploaded images
│   ├── captured/           # Captured images
│   └── processed/          # Processed images
├── templates/              # HTML templates
│   └── index.html          # Main interface
├── script.js               # Client-side JavaScript
├── tests/                  # Test files
│   ├── test_processing.py  # Image processing tests
│   └── test_api.py         # API endpoint tests
└── requirements.txt        # Python dependencies
```

## Image Processing Functions

1. **Rice Grain Detection**
   - Uses watershed algorithm for segmentation
   - Classifies grains as full or broken based on shape and size

2. **Stone Detection**
   - Uses HSV color filtering
   - Validates stone shape using aspect ratio analysis

3. **Husk Detection**
   - Uses HSV color filtering
   - Validates husk shape using aspect ratio analysis

## API Endpoints

- **GET /video_feed** - Live video stream
- **POST /capture** - Capture image from camera
- **POST /process_image** - Process image for object detection

## Testing

### Unit Tests

Run the unit tests with:
```bash
python -m pytest tests/
```

### Image Processing Tests

The system includes comprehensive tests for the image processing algorithms:

1. **Test Images**
   - The `tests/images/` directory contains sample images with known quantities of rice grains, stones, and husk
   - Each test image has an accompanying JSON file with expected detection results

2. **Algorithm Testing**
   - Tests verify the accuracy of detection algorithms across different lighting conditions
   - Detection thresholds are validated using precision and recall metrics

3. **Performance Testing**
   - Tests measure processing time for various image resolutions
   - Memory usage is monitored during batch processing

### Manual Testing

For manually testing image processing quality:

1. Place test images in the `tests/manual/` directory
2. Run the test script:
   ```bash
   python tests/run_manual_tests.py
   ```
3. Review the results in the `tests/manual/results/` directory

## Future Improvements

- Add user authentication
- Implement image export functionality
- Add historical data storage
- Improve detection accuracy with machine learning
- Add mobile-responsive design

## Troubleshooting

- **Camera not detected**: Ensure camera is enabled in raspi-config
- **Permission errors**: Run with `sudo` or configure proper permissions
- **Slow processing**: Reduce image resolution or optimize algorithms
- **Color detection issues**: Calibrate HSV values for your specific lighting conditions

## Contributors

- **Jane Doe** - *Initial project development, image processing algorithms* - [janedoe](https://github.com/janedoe)
- **John Smith** - *Front-end interface, Flask API development* - [johnsmith](https://github.com/johnsmith)
- **Alex Johnson** - *Hardware integration, camera module optimization* - [alexj](https://github.com/alexj)
- **Mary Williams** - *Documentation, testing framework* - [maryw](https://github.com/maryw)
- **Robert Chen** - *Performance optimization, HSV color calibration* - [robchen](https://github.com/robchen)

We welcome contributions! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

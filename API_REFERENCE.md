# API Reference

This document provides a detailed reference for the Flask API endpoints defined in `app.py`.

## Main Application Routes

### `GET /`

- **Description**: Renders the main application page (`index.html`).
- **Methods**: `GET`

### `GET /video_feed`

- **Description**: Provides a video stream from the PiCamera. This is used to display the live feed in the web interface.
- **Methods**: `GET`
- **Response**: A multipart response with JPEG frames.

### `POST /capture`

- **Description**: Captures a single frame from the camera and saves it to the `static/captured` directory.
- **Methods**: `POST`
- **Response**: JSON with the path to the captured image.

    ```json
    { "image_path": "/static/captured/image.jpg" }
    ```

### `POST /process_image`

- **Description**: Takes the path of a captured image and processes it for rice grain analysis using the `detect_and_count_rice_grains` function.
- **Methods**: `POST`
- **Request Body**: JSON with the image path.

    ```json
    { "image_path": "/static/captured/image.jpg" }
    ```

- **Response**: JSON with the analysis results and the path to the processed image.

### `POST /process_dal`

- **Description**: Similar to `/process_image`, but for dal analysis using the `process_dal` function.
- **Methods**: `POST`
- **Request Body**: JSON with the image path.
- **Response**: JSON with the dal analysis results and the path to the processed image.

### `POST /save_results`

- **Description**: Saves the accumulated batch results to a local JSON file.
- **Methods**: `POST`
- **Request Body**: JSON containing the results to be saved.
- **Response**: JSON with a success message.

## WiFi Management Routes

### `GET /wifi`

- **Description**: Renders the WiFi management page (`wifi.html`).
- **Methods**: `GET`

### `GET /wifi/scan`

- **Description**: Scans for available WiFi networks.
- **Methods**: `GET`
- **Response**: JSON list of networks.

### `POST /wifi/connect`

- **Description**: Connects to a specified WiFi network.
- **Methods**: `POST`
- **Request Body**: Form data with `ssid` and `password`.
- **Response**: JSON with connection status.

### `GET /wifi/status`

- **Description**: Gets the current WiFi connection status.
- **Methods**: `GET`
- **Response**: JSON with connection details.

### `POST /wifi/disconnect`

- **Description**: Disconnects from the current WiFi network.
- **Methods**: `POST`
- **Response**: JSON with disconnection status.

## System Routes

### `POST /system/shutdown`

- **Description**: Shuts down the Raspberry Pi.
- **Methods**: `POST`
- **Response**: JSON with a success message.

### `POST /system/restart`

- **Description**: Restarts the Raspberry Pi.
- **Methods**: `POST`
- **Response**: JSON with a success message.

# Project Setup

This guide provides step-by-step instructions to set up the Rice & Dal Analyzer on your Raspberry Pi.

## Prerequisites

Before you begin, ensure you have the following hardware and software:

- **Raspberry Pi**: A Raspberry Pi 4 is recommended for optimal performance.
- **PiCamera**: A Raspberry Pi Camera Module (V2 or later) is required for image capture.
- **SD Card**: A microSD card (16GB or larger) with Raspberry Pi OS (Legacy, 64-bit) installed.
- **Power Supply**: A reliable power supply for your Raspberry Pi.
- **Python**: Python 3.7 or newer.
- **MongoDB Atlas Account**: A free or paid MongoDB Atlas account is needed for cloud data synchronization.

## Installation Steps

### 1. Clone the Repository

Open a terminal on your Raspberry Pi and clone this repository:

```sh
git clone https://github.com/your-username/raspberry-pi-rice-analyzer.git
cd raspberry-pi-rice-analyzer
```

### 2. Install System Dependencies

Install the required system libraries for OpenCV and other dependencies:

```sh
sudo apt-get update
sudo apt-get install -y libgl1-mesa-glx libhdf5-dev libhdf5-serial-dev libatlas-base-dev libjasper-dev libqtgui4 libqt4-test python-picamera2 python-flask
pip install opencv-python
```

*(Note: If a `requirements.txt` file is not available, you can install the packages listed in the `README.md` or infer them from the imports in the Python files.)*

### 3. Configure MongoDB

1. Log in to your [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account.
2. Create a new project and a new cluster.
3. In your cluster, go to **Database Access** and create a new database user with a username and password.
4. Go to **Network Access** and add your Raspberry Pi's IP address to the IP access list. For testing, you can allow access from anywhere by entering `0.0.0.0/0` (this is not recommended for production).
5. Go to **Databases**, click **Connect** on your cluster, select **"Connect your application"**, and copy the connection string.
6. Open the `config.py` file in the project directory:

    ```python
    # config.py
    MONGO_URI = "mongodb+srv://<username>:<password>@<cluster-url>/<database-name>?retryWrites=true&w=majority"
    DB_NAME = "grain_analyzer"
    RICE_COLLECTION = "rice_analysis"
    DAL_COLLECTION = "dal_analysis"
    # ...
    ```

7. Replace `<username>`, `<password>`, `<cluster-url>`, and `<database-name>` with your actual MongoDB credentials.

### 4. Run the Application

Once the setup and configuration are complete, you can start the Flask web server:

```sh
python app.py
```

By default, the application will be accessible at `http://<your-raspberry-pi-ip>:5000`.

---

Next, learn how to use the application in the [**Application Usage (`USAGE.md`)**](./USAGE.md) guide.

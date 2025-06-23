# Database & Syncing

This project features a robust system for storing analysis results both locally and in a remote MongoDB database. This ensures that data is not lost even if the device is offline.

## Local Storage

When you click **"Save Results"**, the current batch of analysis data is saved as a JSON file in the `local_storage` directory. There are separate subdirectories for `rice` and `dal` results.

Each filename includes a timestamp to ensure uniqueness.

## MongoDB Synchronization (`mongodb_sync.py`)

A background process, defined in `mongodb_sync.py`, is responsible for synchronizing the locally stored data with your MongoDB Atlas database.

### How it Works

1.  **Scheduled Task**: A background thread (`schedule_sync_task`) runs periodically (default is every 2 minutes, defined by `SYNC_INTERVAL_SECONDS` in `config.py`).
2.  **Internet Check**: Before attempting to sync, the script checks for an active internet connection.
3.  **Connection to MongoDB**: If there is an internet connection, it attempts to connect to the MongoDB database using the URI from your `config.py` file.
4.  **Data Transfer**: The script scans the `local_storage` directory for any JSON files. For each file, it reads the data, creates a MongoDB document using the schemas in `mongodb_models.py`, and inserts it into the appropriate collection (`rice_analysis` or `dal_analysis`).
5.  **Local File Deletion**: After a file has been successfully synced to MongoDB, it is deleted from the `local_storage` directory to prevent duplicate entries.

### Standalone Sync Script (`mongo_sync_standalone.py`)

In addition to the automatic background sync, there is a standalone script `mongo_sync_standalone.py` that can be run manually from the command line to perform a one-time sync.

---

Next, see the [**API Reference (`API_REFERENCE.md`)**](./API_REFERENCE.md) for detailed documentation of the Flask API.

# WiFi Management

This application includes a WiFi management interface to help you connect your Raspberry Pi to a wireless network without needing to use the command line. This is especially useful if you are using the device with a touchscreen.

## Accessing the WiFi Page

You can access the WiFi management page by clicking the **"Utils"** button on the main analyzer page or by navigating directly to `/wifi`.

## Features

- **Scan for Networks**: The "Scan for Networks" button will search for all available WiFi networks within range and display them in a list.
- **Connect to a Network**: Clicking on a network in the list will reveal a password input field. Enter the password and click "Connect".
- **View Connection Status**: The page will display the current network connection status, including the SSID (network name) and the IP address.
- **Disconnect**: If you are connected to a network, a "Disconnect" button will be available.
- **Virtual Keyboard**: A virtual keyboard is provided for entering the WiFi password on a touchscreen.

## Technical Implementation (`wifi_manager.py`)

The backend for the WiFi functionality is handled by `wifi_manager.py`. This script uses the `nmcli` command-line tool, which is the command-line interface for NetworkManager.

- **Scanning**: It uses `nmcli dev wifi list` to get a list of available networks.
- **Connecting**: It uses `nmcli dev wifi connect <SSID> password <password>` to establish a connection.
- **Status**: It parses the output of `nmcli con show --active` to get the current connection details.
- **Disconnecting**: It uses `nmcli con down <connection-name>` to disconnect from the current network.

*(Note: The code also includes a fallback to `wpa_supplicant` if NetworkManager is not available, but `nmcli` is the primary method.)*

---

Next, learn how data is stored and synchronized in the [**Database & Syncing (`DATABASE.md`)**](./DATABASE.md) guide.

# Power Controller

Power Controller is a Python application designed to manage power settings based on certain conditions. It can be run as a Windows service.

## Requirements

- Python 3.x
- `pip` (Python package installer)
- `nssm` (Non-Sucking Service Manager)

## Installation

1. **Clone the repository**:
    ```sh
    git clone https://github.com/yourusername/power-controller.git
    cd power-controller
    ```

2. **Create a virtual environment**:
    ```sh
    python -m venv venv
    ```

3. **Activate the virtual environment**:
    - On Windows:
        ```sh
        .\venv\Scripts\activate
        ```
    - On Unix or MacOS:
        ```sh
        source venv/bin/activate
        ```

4. **Install the required packages**:
    ```sh
    pip install -r requirements.txt
    ```

## Running as a Windows Service

1. **Prepare the service**:
    - Open a command prompt with administrative privileges.
    - Run the [`install.bat`](./install.bat) script:
        ```sh
        install.bat
        ```

    The [`install.bat`](c:/pwrcon/install.bat) script performs the following actions:
    - Stops the existing `pwrcon` service if it is running.
    - Deletes the existing `pwrcon` service.
    - Installs the required Python packages.
    - Uses `pyinstaller` to create an executable from `pwrcon.py`.
    - Installs the `pwrcon` service using `nssm`.

2. **Start the service**:
    ```sh
    nssm start pwrcon
    ```

## Configuration

The application uses a configuration file ([`config.json`](c:/pwrcon/config.json)) to manage settings. Below are the configuration options available:

This JSON configuration file is used for setting up the power control application. Below are the details of each field:

- `device_config_file`: Path to the device configuration file.
- `log_file`: Path to the log file.
- `log_to_file`: Boolean flag to enable or disable logging to a file.
- `mac`: MAC address of the device.
- `username`: Username for authentication.
- `password`: Password for authentication.
- `ip`: IP address of the device - devices will be scanned if connection fails.
- `interval`: Interval in seconds for the power control checks.
- `th_low`: Lower threshold battery % level.
- `th_high`: Upper threshold battery % level.
- `always_on_processes`: If these processes are running, power will stay on.
- `power_on_start`: Boolean flag to power on the device at service start.

```json
{
  "device_config_file": "c:\\pwrcon\\.device",
  "log_file": "c:\\pwrcon\\pwrcon.log",
  "log_to_file": false,
  "mac": "60:83:E7:15:2A:14",
  "username": "user",
  "password": "password",
  "ip": "192.168.50.193",
  "interval": 10,
  "th_low": 20,
  "th_high": 80,
  "always_on_processes": [ "VALORANT.exe" ],
  "power_on_start": true
}
```

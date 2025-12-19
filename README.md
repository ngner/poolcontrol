# poolcontrol
Simple Python program to control solar pool pump via TP Link Smart WiFi plug using a raspberry pi and cheap DS18B20 temp sensors

## Background

You will need a raspberry pi, a TPLink HS100/110, and two DS18B20 temperature sensors - and a pump of course.

## Setup

1. Install required Python packages. On Debian Bookworm (Raspberry Pi OS Bookworm), use one of these methods:

   **Option A: Check if packages are available via apt (recommended first):**
   ```bash
   sudo apt update
   sudo apt install python3-pyhs100 python3-yaml
   ```
   
   **Option B: If not available via apt, use Python's built-in pip module:**
   ```bash
   sudo python3 -m pip install pyHS100 pyyaml
   ```
   
   **Note:** On modern Debian/Ubuntu systems, `python3 -m pip` is preferred over `pip` as it uses Python's built-in pip module and doesn't require pip to be installed separately.

2. Clone this repo to `/usr/local/poolcontrol/` on your Pi:
   ```bash
   sudo mkdir -p /usr/local/poolcontrol
   sudo git clone <repository-url> /usr/local/poolcontrol
   # Or if you already have it elsewhere:
   # sudo cp -r /path/to/poolcontrol/* /usr/local/poolcontrol/
   ```

3. Create a dedicated user for the service (optional but recommended):
   ```bash
   sudo useradd -r -s /bin/false poolcontrol
   sudo chown -R poolcontrol:poolcontrol /usr/local/poolcontrol
   ```
   **Note:** If you prefer to run as a different user (e.g., `pi` or `nick`), edit `poolcontrol.service` and change the `User=` line accordingly.

4. Copy `poolControl.yaml` to `/etc/poolControl.yaml`:
   ```bash
   sudo cp /usr/local/poolcontrol/poolControl.yaml /etc/poolControl.yaml
   ```

5. Edit `/etc/poolControl.yaml` and configure:
   - `equipment.poolPlugAddress`: IP address of your TP-Link smart plug
   - `equipment.sensors`: Addresses of your DS18B20 sensors
   - `logging.database`: Path to SQLite database file (e.g., `/var/lib/poolcontrol/poolcontrol.db` or `/home/poolcontrol/poolcontrol.db`)
   - `control.targetPoolTemp`: Target pool temperature in Celsius
   - `control.requiredGain`: Minimum temperature difference (roof - pool) to run pump

6. Create database directory and set permissions (if using a custom database path):
   ```bash
   sudo mkdir -p /var/lib/poolcontrol
   sudo chown poolcontrol:poolcontrol /var/lib/poolcontrol
   # Or if using home directory:
   # sudo mkdir -p /home/poolcontrol
   # sudo chown poolcontrol:poolcontrol /home/poolcontrol
   ```

7. Copy the systemd service file:
   ```bash
   sudo cp /usr/local/poolcontrol/poolcontrol.service /etc/systemd/system/poolcontrol.service
   sudo systemctl daemon-reload
   sudo systemctl enable poolcontrol.service
   sudo systemctl start poolcontrol.service
   ```

8. Verify the service is running:
   ```bash
   sudo systemctl status poolcontrol.service
   sudo journalctl -u poolcontrol.service -f
   ```

## Data Storage

The system stores timeseries data in a SQLite database. The database contains a `readings` table with:
- `Epoch`: Unix timestamp (INTEGER PRIMARY KEY)
- `roofTemp`: Roof sensor temperature in Celsius (REAL)
- `poolTemp`: Pool sensor temperature in Celsius (REAL)
- `pumpNeed`: Boolean flag indicating if pump should run (INTEGER: 0 or 1)
- `pumpState`: Actual pump state (INTEGER: -1=fail, 0=off, 1=on)

The database file path is configured in `/etc/poolControl.yaml` under `logging.database`.

## Debug Tools

See the `debugtools/` directory for utilities to monitor and debug the database:
- `tail_db.py`: Python script to view recent entries (supports follow mode)
- `tail-db.sh`: Shell script to follow database entries with formatted output

See `debugtools/README.md` for detailed usage instructions.

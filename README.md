# poolcontrol
Simple Python program to control solar pool pump via TP Link Smart WiFi plug using a raspberry pi and cheap DS18B20 temp sensors

## Background

You will need a raspberry pi, a TPLink HS100/110, and two DS18B20 temperature sensors - and a pump of course.

## Setup

1. Download and install the `pyHS100` python module:
   ```bash
   pip install pyHS100
   ```

2. Clone this repo to `/usr/local/poolcontrol/` on your Pi.

3. Copy `poolControl.yaml` to `/etc/poolControl.yaml`:
   ```bash
   sudo cp poolControl.yaml /etc/poolControl.yaml
   ```

4. Edit `/etc/poolControl.yaml` and configure:
   - `equipment.poolPlugAddress`: IP address of your TP-Link smart plug
   - `equipment.sensors`: Addresses of your DS18B20 sensors
   - `logging.database`: Path to SQLite database file (default: `/home/nick/poolcontrol.db`)
   - `control.targetPoolTemp`: Target pool temperature in Celsius
   - `control.requiredGain`: Minimum temperature difference (roof - pool) to run pump

5. Copy the systemd service file:
   ```bash
   sudo cp poolcontrol.service /etc/systemd/system/poolcontrol.service
   sudo systemctl daemon-reload
   sudo systemctl enable poolcontrol.service
   sudo systemctl start poolcontrol.service
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

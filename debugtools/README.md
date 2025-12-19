# Debug Tools

This directory contains debugging utilities for monitoring the pool control database.

## Tools

### tail_db.py

Python script for viewing recent database entries, similar to `tail` for files.

**Usage:**
```bash
# Show last 20 entries (default)
./tail_db.py

# Follow mode - continuously show new entries (like tail -f)
./tail_db.py -f

# Show last 50 entries
./tail_db.py -n 50

# Use custom database path
./tail_db.py /path/to/poolcontrol.db -f
```

**Options:**
- `-f, --follow`: Follow mode - continuously display new entries as they're added
- `-n, --lines N`: Number of recent entries to show (default: 20)
- Database path: Optional first argument (default: `/var/lib/poolcontrol/poolcontrol.db`)

**Output Format:**
```
Epoch,roofTemp,poolTemp,pumpNeed,pumpState
1699123456,32.50,28.30,1,on
1699123516,32.45,28.35,1,on
```

Where:
- `Epoch`: Unix timestamp
- `roofTemp`: Roof sensor temperature (°C)
- `poolTemp`: Pool sensor temperature (°C)
- `pumpNeed`: Boolean (0 or 1) - whether pump should run
- `pumpState`: State string ('fail', 'off', or 'on')

### tail-db.sh

Shell script for following database entries with formatted output.

**Usage:**
```bash
# Follow mode with default database
./tail-db.sh

# Follow mode with custom database path
./tail-db.sh /path/to/poolcontrol.db
```

**Output:**
Displays entries in a formatted table with column headers and human-readable timestamps. Continuously updates showing new entries as they're added to the database.

## Database Schema

The database contains a `readings` table with the following columns:

- `Epoch` (INTEGER PRIMARY KEY): Unix timestamp
- `roofTemp` (REAL): Roof sensor temperature in Celsius
- `poolTemp` (REAL): Pool sensor temperature in Celsius
- `pumpNeed` (INTEGER): Boolean flag - 0 = false, 1 = true
- `pumpState` (INTEGER): Pump state - -1 = fail, 0 = off, 1 = on

## Requirements

- Python 3 (for `tail_db.py`)
- sqlite3 command-line tool (for `tail-db.sh`)
- Access to the pool control database file


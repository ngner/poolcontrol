#!/bin/bash
DB_FILE="${1:-/var/lib/poolcontrol/poolcontrol.db}"
LAST_EPOCH=0

while true; do
    # Get new rows since last check
    sqlite3 -header -column "$DB_FILE" \
        "SELECT datetime(Epoch, 'unixepoch', 'localtime') as Time, 
                roofTemp, poolTemp, pumpNeed, pumpState 
         FROM readings 
         WHERE Epoch > $LAST_EPOCH 
         ORDER BY Epoch;"
    
    # Update last epoch
    LAST_EPOCH=$(sqlite3 "$DB_FILE" "SELECT MAX(Epoch) FROM readings;")
    
    sleep 1
done


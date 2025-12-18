#!/usr/bin/env python3
import sqlite3
import time
import sys
import argparse
from datetime import datetime

def tail_database(db_path, follow=False, lines=20):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    last_epoch = 0
    
    # Get initial lines
    if not follow:
        cursor.execute("""
            SELECT Epoch, roofTemp, poolTemp, pumpNeed, pumpState 
            FROM readings 
            ORDER BY Epoch DESC 
            LIMIT ?
        """, (lines,))
        rows = cursor.fetchall()
        for row in reversed(rows):
            print(format_row(row))
        return
    
    # Follow mode
    while True:
        cursor.execute("""
            SELECT Epoch, roofTemp, poolTemp, pumpNeed, pumpState 
            FROM readings 
            WHERE Epoch > ? 
            ORDER BY Epoch
        """, (last_epoch,))
        
        rows = cursor.fetchall()
        for row in rows:
            print(format_row(row))
            last_epoch = row[0]
        
        time.sleep(1)

def format_row(row):
    epoch, roof, pool, need, state = row
    time_str = datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')
    state_map = {-1: 'fail', 0: 'off', 1: 'on'}
    return f"{epoch},{roof:.2f},{pool:.2f},{need},{state_map[state]}"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Tail pool control database')
    parser.add_argument('database', nargs='?', default='/home/nick/poolcontrol.db',
                       help='Database file path')
    parser.add_argument('-f', '--follow', action='store_true',
                       help='Follow mode (like tail -f)')
    parser.add_argument('-n', '--lines', type=int, default=20,
                       help='Number of lines to show (default: 20)')
    
    args = parser.parse_args()
    tail_database(args.database, args.follow, args.lines)


#!/usr/bin/env python

from pyHS100 import SmartPlug, Discover
from ruamel.yaml import YAML

import time
import sys
import sqlite3




## Get configuration from file if possible
yaml = YAML(typ='safe')
try:
    with open("/etc/poolControl.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile)
except:
    # If this fails use an emptyish config dict.
    config = { 'logging': {}, 'equipment': {}, 'control': {} }
    print("No config file found at /etc/poolControl.yaml using default settings")

database = config['logging'].get('database') or "/home/nick/poolcontrol.db"
poolPlugAddress = config['equipment'].get('poolPlugAddress') or "192.168.178.210"

#set out sensor addresses
sensors = config["equipment"].get("sensors") or {}

if len(sensors) == 0:
    sensors = { 
           "roof": {"address" : "28-021313aad3aa"},
           "pool": {"address" : "28-021317db8eaa"}
          }
         

targetPoolTemp = config["control"].get("targetPoolTemp") or 27           
requiredGain = config["control"].get("requiredGain") or 10  #Centrigade difference to constitute effiecent heating


print('Running with database:{0} and poolPlugAddress:{1} and targetPoolTemp:{2} and requiredGain:{3} and Sensors {4}'.format(database, poolPlugAddress, targetPoolTemp, requiredGain, sensors)) 



pumpRun = 0

poolPlug = SmartPlug(poolPlugAddress)


def initDatabase():
    """Initialize SQLite database with readings table if it doesn't exist"""
    conn = sqlite3.connect(database)
    tsdb = conn.tsdb()
    
    # Check if table already exists
    tsdb.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='readings'
    """)
    
    if tsdb.fetchone() is None:
        # Table doesn't exist, create it
        create_table_sql = """
        CREATE TABLE readings (
            Epoch INTEGER PRIMARY KEY,
            roofTemp REAL NOT NULL,
            poolTemp REAL NOT NULL,
            pumpNeed INTEGER NOT NULL CHECK(pumpNeed IN (0, 1)),
            pumpState INTEGER NOT NULL CHECK(pumpState IN (-1, 0, 1))
        )
        """
        tsdb.execute(create_table_sql)
        tsdb.execute("CREATE INDEX idx_epoch ON readings(Epoch)")
        conn.commit()
        print("Database initialized at: {0}".format(database), flush=True)
    
    conn.close()


def checkTemp():
    for sensorname in sensors:
        address = sensors[sensorname]["address"]
        tempfile = open("/sys/bus/w1/devices/" + address + "/temperature")  # Older versions of Pi /sys/devices/w1_bus_master1/" + address + "/w1_slave"
        tempdata = tempfile.read()
        tempfile.close()
        # convert string with data to the temp as a float
        # example of contents "1d 02 4b 46 7f ff 0c 10 9a : crc=9a YES\n1d 02 4b 46 7f ff 0c 10 9a t=33812\n"
        temp = float(tempdata.rstrip().split()[-1].lstrip('t='))
        #convert the temp to Degrees celcius
        temp = temp / 1000
        sensors[sensorname]["temp"] = temp
    #print(sensors)
    return


def writeTemp():
    """Write temperature readings to SQLite database"""
    epoch = int(time.time())
    
    # Get temperatures from sensors (expecting 'roof' and 'pool' sensors)
    roofTemp = sensors.get("roof", {}).get("temp", 0.0)
    poolTemp = sensors.get("pool", {}).get("temp", 0.0)
    
    # pumpNeed is boolean: 1 if pumpRun is 1, 0 otherwise
    pumpNeed = 1 if pumpRun == 1 else 0
    
    # Get pumpState: 0=off, 1=on, -1=fail
    pumpState = -1  # Default to fail state
    try:
        currentState = poolPlug.state
        if currentState == "OFF":
            pumpState = 0
        elif currentState == "ON":
            pumpState = 1
    except:
        print("poolControl failed to reach poolPlug", flush=True)
        pumpState = -1
    
    # Insert into database
    conn = sqlite3.connect(database)
    tsdb = conn.tsdb()
    tsdb.execute(
        "INSERT INTO readings (Epoch, roofTemp, poolTemp, pumpNeed, pumpState) VALUES (?, ?, ?, ?, ?)",
        (epoch, roofTemp, poolTemp, pumpNeed, pumpState)
    )
    conn.commit()
    conn.close()

    return

def checkSolarGain(roofTemp=0, poolTemp=0):
    global pumpRun
    gain = roofTemp - poolTemp
    #print("gain =", gain)
    if gain >= requiredGain:
        #print("We have enough gain to run:", gain)
        if poolTemp <= targetPoolTemp:
            #print(" and Pooltemp requires pump on:", targetPoolTemp)
            pumpRun = 1
        else:
            pumpRun = 0
            #print("Stop due to poolTemp", poolTemp)
    else:
        pumpRun = 0
        #print("Stop due to lack of gain:", gain)
    #print("check gain with:", roofTemp, poolTemp, pumpRun)
    return pumpRun

def pumpControl():
    global pumpRun
    if pumpRun == 1:
        try: 
            if poolPlug.state == "OFF":
                print("starting pump", flush=True )
                poolPlug.turn_on()
        except:
            print("poolControl failed to reach poolPlug", flush=True )
            #TODO: Send ALert some how
       
    else:
        #print("maybe we should stop the pump")
        #print("poolPlug State =", poolPlug.state)
        try:
            if poolPlug.state == "ON":
                print("stopping pump", flush=True )
                poolPlug.turn_off()
        except:
            print("poolControl failed to reach poolPlug", flush=True )
            sys.stdout.flush()
            #TODO: Send ALert some how
    return
        

try:
    # Initialize database on startup
    initDatabase()
    
    while True:
        checkTemp()
        checkSolarGain(roofTemp=sensors["roof"]["temp"], poolTemp=sensors["pool"]["temp"])
        #print("current pumpRun", pumpRun)
        pumpControl()
        writeTemp()
        time.sleep(60)


except KeyboardInterrupt:
    pumpRun = 0
    pumpControl()
    print("Program Exited Cleanly", flush=True )
    

#!/usr/bin/env python

from pyHS100 import SmartPlug, Discover
from ruamel.yaml import YAML

import time
import sys




## Get configuration from file if possible
yaml = YAML(typ='safe')
try:
    with open("/etc/poolControl.yaml", "r") as yamlfile:
        config = yaml.load(yamlfile)
except:
    # If this fails use an emptyish config dict.
    config = { 'logging': {}, 'equipment': {}, 'control': {} }
    print("No config file found at /etc/poolControl.yaml using default settings")

logfile = config['logging'].get('logfile') or "/home/nick/timeseriesTest.csv"
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


print('Running with logfile:{0} and poolPlugAddress:{1} and targetPoolTemp:{2} and requiredGain:{3} and Sernsors {4}'.format(logfile, poolPlugAddress, targetPoolTemp, requiredGain, sensors)) 



logfile 
pumpRun = 0

poolPlug = SmartPlug(poolPlugAddress)


def checkTemp():
    for sensorname in sensors:
        address = sensors[sensorname]["address"]
        tempfile = open("/sys/devices/w1_bus_master1/" + address + "/w1_slave")
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
    timeseries = open(logfile, "a")
    timestamp = str(int(time.time()))
    reading = timestamp + ","
    for name in sensors:
        reading +=  str(sensors[name]["temp"]) + ","
        #print(reading)
    reading += str(pumpRun) + ","
    try:
        currentState = poolPlug.state
        if  currentState == "OFF":
            reading += "0,"
        if currentState == "ON":
            reading += "1,"
    except:
        print("poolControl failed to reach poolPlug", flush=True )
        reading += "-1,"
    reading += "\n"
    #print(reading)
    timeseries.write(reading)
    timeseries.close()

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
    
    timeseries = open(logfile, "a")
    if (timeseries.tell() == 0):
        print("Time Series file does not exist adding CSV headers", flush=True )
        timeseries.write("Time" + "," + ",".join(sorted(sensors.keys())) + "\n")
    timeseries.close()
    
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
    timeseries.close()
    print("Program Exited Cleanly", flush=True )
    

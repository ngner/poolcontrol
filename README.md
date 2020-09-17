# poolcontrol
Simple Python program to control solar pool pump via TP Link Smart WiFi plug using a raspberry pi and cheap DS18B20 temp sensors

#Background

You will need a raspberry pi a TPLink HS100/110 and two DS18B20 - and a pump of course.

# Setup
Download and install the pyHS100 python module
Clone this repo to /usr/local/poolcontrol/  on your Pi.
Copy the poolcontrol.yaml to /etc/poolControl.yaml
Check out the settings in the file and alter as required for solar gain, max temperature etc.

Copy the systemd service file to:
/etc/systemd/system/poolcontrol.service

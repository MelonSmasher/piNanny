#!/usr/bin/env python3

from libpinanny import c2f, debugOutCFH
import time
import os
import socketio
import Adafruit_DHT

debug = os.environ.get('DEBUG', False)
# Create the second sensor
sensor = str(os.environ.get('GPIO_SENSOR_2ND', "AM2302")).upper()
sensor_name = sensor
sensor_pin = int(os.environ.get('GPIO_PIN_2ND', 5))

# Let let the socket io server fire up first
print('[' + sensor_name + ']: Waiting for Socket IO server to fire up.\n')
time.sleep(15)

# Create the sio client
sio = socketio.Client()
# Connect to the sio server
sio.connect('http://localhost:' + str(os.environ.get('EXPRESS_PORT', 80)))

if sensor == 'DHT22':
    sensor = Adafruit_DHT.DHT22
elif sensor == 'DHT11':
    sensor = Adafruit_DHT.DHT11
elif sensor == 'AM2302':
    sensor = Adafruit_DHT.AM2302
else:
    print('[' + sensor_name + ']: Please supply a valid GPIO SENSOR value (DHT11/DHT22/AM2302).\n')
    exit(1)

try:
    while True:
        # Poll the probe
        humidity, temperature = Adafruit_DHT.read_retry(sensor, int(sensor_pin))

        if humidity is not None and temperature is not None:
            # If debug is enabled output the values to stdout
            if debug:
                debugOutCFH(sensor_name, temperature, c2f(temperature), humidity)

            if humidity <= 100:  # If we have a garbage humidity reading skip sleep and poll again
                # Send the data to the SIO server
                sio.emit('SensorReadingAm2302',
                         {
                             "temp_c": temperature,
                             "temp_f": c2f(temperature),
                             "humidity": humidity,
                         })
                # Sleep
                time.sleep(int(os.environ.get('SENSOR_READ_INTERVAL', 10)))
            else:
                print('[' + sensor_name + ']: Odd humidity reading: ' + humidity + '%\n')
                time.sleep(1)
        else:
            print('[' + sensor_name + ']: Temp and/or Humidity came back null.\n')
            # Sleep
            time.sleep(int(os.environ.get('SENSOR_READ_INTERVAL', 10)))

except KeyboardInterrupt:
    pass

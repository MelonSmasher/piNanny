#!/usr/bin/env python3

import time
import os
import json

import socketio
import bme680

time.sleep(3)

try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

sio = socketio.Client()
sio.connect('http://localhost:' + str(os.environ['EXPRESS_PORT']))

# These calibration data can safely be commented
# out, if desired.

print('Calibration data:')
for name in dir(sensor.calibration_data):

    if not name.startswith('_'):
        value = getattr(sensor.calibration_data, name)

        if isinstance(value, int):
            print('{}: {}'.format(name, value))

# These oversampling settings can be tweaked to
# change the balance between accuracy and noise in
# the data.

sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

print('\n\nInitial reading:')
for name in dir(sensor.data):
    value = getattr(sensor.data, name)

    if not name.startswith('_'):
        print('{}: {}'.format(name, value))

sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

print('\n\nPolling sensor:')
try:
    while True:
        if sensor.get_sensor_data():
            data = sensor.data
            sio.emit('SensorReading',
                     {"temperature": data.temperature, "pressure": data.pressure, "humidity": data.humidity,
                      "gas_resistance": data.gas_resistance})
            time.sleep(1)

except KeyboardInterrupt:
    pass

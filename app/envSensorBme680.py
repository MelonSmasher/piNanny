#!/usr/bin/env python3

import time
import os

import socketio
import bme680


# Converts celsius temps to fahrenheit
def c2f(celsius):
    return (9.0 / 5) * celsius + 32


print('Waiting for Socket IO server to fire up.\n')
# Let let the socket io server fire up first
time.sleep(5)

# Create the sio client
sio = socketio.Client()
# Connect to the sio server
sio.connect('http://localhost:' + str(os.environ['EXPRESS_PORT']))

# Create the BME sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# Set the sensor properties
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Burn in vars
start_time = time.time()
curr_time = time.time()
burn_in_time = 300
burn_in_data = []

try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    print('Collecting gas resistance burn-in data for 5 mins\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)
    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = 40.0
    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25
    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))
    while True:
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            # Store the data
            data = sensor.data

            # Calculate the IAQ index
            gas = data.gas_resistance
            gas_offset = gas_baseline - gas
            hum = data.humidity
            hum_offset = hum - hum_baseline

            # Calculate hum_score as the distance from the hum_baseline.
            if hum_offset > 0:
                hum_score = (100 - hum_baseline - hum_offset)
                hum_score /= (100 - hum_baseline)
                hum_score *= (hum_weighting * 100)
            else:
                hum_score = (hum_baseline + hum_offset)
                hum_score /= hum_baseline
                hum_score *= (hum_weighting * 100)

            # Calculate gas_score as the distance from the gas_baseline.
            if gas_offset > 0:
                gas_score = (gas / gas_baseline)
                gas_score *= (100 - (hum_weighting * 100))
            else:
                gas_score = 100 - (hum_weighting * 100)

            # Calculate air_quality_score.
            air_quality_score = hum_score + gas_score

            # Send the data to the SIO server
            sio.emit('SensorReading',
                     {
                         "temperature_c": data.temperature,
                         "temperature_f": c2f(data.temperature),
                         "pressure": data.pressure,
                         "humidity": data.humidity,
                         "gas_resistance": data.gas_resistance,
                         "iaq": air_quality_score
                     })
            time.sleep(1)

except KeyboardInterrupt:
    pass

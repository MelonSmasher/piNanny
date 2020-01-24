#!/usr/bin/env python3

from libpinanny import c2f, debugOutCFH, get_cpu_temperature
import time
import os
import socketio
import bme680

debug = os.environ.get('DEBUG', False)

# Let let the socket io server fire up first
print('[BME680]: Waiting for Socket IO server to fire up.\n')
time.sleep(15)

# Create the sio client
sio = socketio.Client()
# Connect to the sio server
sio.connect('http://localhost:' + str(os.environ.get('EXPRESS_PORT', 80)))

# Create the BME sensor
try:
    sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
except IOError:
    sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)

# Set the sensor properties
sensor.set_humidity_oversample(bme680.OS_8X)
sensor.set_pressure_oversample(bme680.OS_8X)
sensor.set_temperature_oversample(bme680.OS_16X)
sensor.set_filter(bme680.FILTER_SIZE_3)

sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)

# Burn in vars
start_time = time.time()
curr_time = time.time()
burn_in_time = int(os.environ.get('BME680_SENSOR_BURNIN_TIME', 300))  # Burn in time in seconds
burn_in_data = []

# Temp compensation vars
smooth_size = int(os.environ.get('CPU_TEMP_JITTER_DAMPENER', 10))  # Dampens jitter due to rapid CPU temp changes
factor = float(os.environ.get('BME680_CPU_TEMP_COMP_FACTOR', 1.0))
cpu_temps = []

try:
    # Collect gas resistance burn-in values, then use the average
    # of the last 50 values to set the upper limit for calculating
    # gas_baseline.
    print('Collecting gas resistance burn-in data for ' + str(burn_in_time) + ' seconds\n')
    while curr_time - start_time < burn_in_time:
        curr_time = time.time()
        if sensor.get_sensor_data() and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            burn_in_data.append(gas)
            print('Gas: {0} Ohms'.format(gas))
            time.sleep(1)
    gas_baseline = sum(burn_in_data[-50:]) / 50.0
    # Set the humidity baseline to 40%, an optimal indoor humidity.
    hum_baseline = float(os.environ.get('HUMIDITY_BASELINE', 40.0))
    # This sets the balance between humidity and gas reading in the
    # calculation of air_quality_score (25:75, humidity:gas)
    hum_weighting = 0.25
    print('Gas baseline: {0} Ohms, humidity baseline: {1:.2f} %RH\n'.format(
        gas_baseline,
        hum_baseline))
    while True:

        # If debug is enabled output the values to stdout
        if debug:
            sensor.get_sensor_data()
            debugOutCFH('BME680', sensor.data.temperature, c2f(sensor.data.temperature), sensor.data.humidity)

        if sensor.get_sensor_data() and sensor.data.heat_stable:

            # Get and store the current CPU temp
            cpu_temp = get_cpu_temperature()
            cpu_temps.append(cpu_temp)
            # Trim the cpu_temps array if needed
            if len(cpu_temps) > smooth_size:
                cpu_temps = cpu_temps[1:]
            # Determine a more regular CPU temp
            smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))
            raw_temp = sensor.data.temperature
            comp_temp = raw_temp - ((smoothed_cpu_temp - raw_temp) / factor)

            # Calculate the IAQ index
            hum = sensor.data.humidity
            gas = sensor.data.gas_resistance
            gas_offset = gas_baseline - gas
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
            sio.emit('SensorReadingBme680',
                     {
                         "temp_c": comp_temp,
                         "temp_f": c2f(comp_temp),
                         "temp_raw_c": sensor.data.temperature,
                         "temp_raw_f": c2f(sensor.data.temperature),
                         "pressure": sensor.data.pressure,
                         "humidity": hum,
                         "gas_resistance": sensor.data.gas_resistance,
                         "iaq": air_quality_score
                     })
            time.sleep(int(os.environ.get('SENSOR_READ_INTERVAL', 10)))

except KeyboardInterrupt:
    pass

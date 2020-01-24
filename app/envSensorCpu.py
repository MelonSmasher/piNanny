#!/usr/bin/env python3

from libpinanny import c2f, get_cpu_temperature, debugOutCF
import time
import os
import socketio

debug = os.environ.get('DEBUG', False)

# Let let the socket io server fire up first
print('[CPU]: Waiting for Socket IO server to fire up.\n')
time.sleep(15)

# Create the sio client
sio = socketio.Client()
# Connect to the sio server
sio.connect('http://localhost:' + str(os.environ.get('EXPRESS_PORT', 80)))

# Temp compensation vars
smooth_size = int(os.environ.get('CPU_TEMP_JITTER_DAMPENER', 10))  # Dampens jitter due to rapid CPU temp changes
cpu_temps = []

try:
    while True:
        # Get and store the current CPU temp
        cpu_temp = get_cpu_temperature()
        cpu_temps.append(cpu_temp)
        # Trim the cpu_temps array if needed
        if len(cpu_temps) > smooth_size:
            cpu_temps = cpu_temps[1:]
        # Determine a more regular CPU temp
        smoothed_cpu_temp = sum(cpu_temps) / float(len(cpu_temps))

        # If debug is enabled output the values to stdout
        if debug:
            debugOutCF('CPU', smoothed_cpu_temp, c2f(smoothed_cpu_temp))

        # Send the data to the SIO server
        sio.emit('SensorReadingCPU',
                 {
                     "temp_c": smoothed_cpu_temp,
                     "temp_f": c2f(smoothed_cpu_temp)
                 })
        time.sleep(int(os.environ.get('SENSOR_READ_INTERVAL', 10)))

except KeyboardInterrupt:
    pass

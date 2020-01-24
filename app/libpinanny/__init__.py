from subprocess import PIPE, Popen


# Converts celsius temps to fahrenheit
def c2f(celsius):
    return (9.0 / 5) * celsius + 32


# Gets the CPU temperature in degrees C
def get_cpu_temperature():
    process = Popen(['vcgencmd', 'measure_temp'], stdout=PIPE)
    output, _error = process.communicate()
    return float(str(str(output).split('=')[1]).split("'")[0])


def debugOutCFH(sensor, valueC, valueF, valueH):
    print('Debug Values [' + sensor + ']:')
    print('C: ' + str(valueC))
    print('F: ' + str(valueF))
    print('H: ' + str(valueH) + '%')
    print('')


def debugOutCF(sensor, valueC, valueF):
    print('Debug Values [' + sensor + ']:')
    print('C: ' + str(valueC))
    print('F: ' + str(valueF))
    print('')

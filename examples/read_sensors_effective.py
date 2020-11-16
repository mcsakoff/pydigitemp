import time
from digitemp.master import UART_Adapter
from digitemp.device import TemperatureSensor
from digitemp.exceptions import OneWireException

bus = UART_Adapter('/dev/ttyS0')

sensors = []
for rom in bus.get_connected_ROMs():
    try:
        sensors.append(TemperatureSensor(bus, rom))
    except OneWireException:
        pass

print(55 * "=")
for sensor in sensors:
    sensor.info()
    print(55 * "=")

# Instead of calling sensor.get_temperature() for each sensor we call bus.measure_temperature_all() once
# and then do sensor.read_temperature() for each sensor.

try:
    while True:
        measurements = []
        bus.measure_temperature_all()
        for sensor in sensors:
            try:
                measurements.append("%3.02fºC" % sensor.read_temperature())
            except OneWireException:
                measurements.append("  error")
        print("   ".join(measurements))
        time.sleep(3)
except KeyboardInterrupt:
    pass
finally:
    bus.close()

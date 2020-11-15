#
# This example demonstrates how to organize temperature reading in infinite loop
# with proper exceptions handling.
#
import time
from digitemp.master import UART_Adapter
from digitemp.device import TemperatureSensor
from digitemp.exceptions import DeviceError, AdapterError

bus = None
device = "/dev/ttyS0"
sensID = "10A75CA80208001A"

# infinite device loop
while True:
    try:
        time.sleep(3)
        print(f"Connecting to '{device}'...")
        bus = UART_Adapter(device)
        print("Connected to '%s'..." % device)

        sensor = TemperatureSensor(bus, rom=sensID)
        # infinite reading loop
        while True:
            try:
                temp = sensor.get_temperature()
                print(f"{temp}ºC")
            except AdapterError:
                print("U")
            time.sleep(3)

    except AssertionError:
        bus.close()
        bus = None
    except DeviceError:
        bus = None
    except KeyboardInterrupt:
        print("Done...")
        break

if bus is not None:
    print("Closing '%s'..." % device)
    bus.close()
    print("Closed '%s'..." % device)

from digitemp.master import UART_Adapter
from digitemp.device import AddressableDevice

bus = UART_Adapter('/dev/ttyS0')

for rom in AddressableDevice(bus).get_connected_ROMs():
    print(rom)

bus.close()

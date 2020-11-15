from digitemp.master import UART_Adapter

bus = UART_Adapter('/dev/ttyS0')

for rom in bus.get_connected_ROMs():
    print(rom)

bus.close()

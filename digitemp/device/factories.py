from ..master import UART_Adapter
from .thermometer import OneWireTemperatureSensor, DS18S20, DS18B20, DS1822
from ..exceptions import OneWireException
from ..utils import *

if PY3:
    from typing import Optional

__temperatureSensors = {
    0x10: DS18S20,
    0x22: DS1822,
    0x28: DS18B20,
}


def TemperatureSensor(bus, rom=None):
    """
    If rom is not, will try to find a connected device.
    In that case there must be only one device connected.
    """
    # type: (UART_Adapter, Optional[str]) -> OneWireTemperatureSensor
    if rom is None:
        roms = bus.get_connected_ROMs()
        if len(roms) > 1:
            raise OneWireException(f"More than one connected 1-wire device found: {', '.join(roms)}")
        rom = roms[0]
    family_code = iord(str2rom(rom), 0)
    if family_code not in __temperatureSensors:
        raise OneWireException("Unsupported family code: %d" % family_code)
    return __temperatureSensors[family_code](bus, rom=rom)

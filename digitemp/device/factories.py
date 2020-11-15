from ..master import UART_Adapter
from .thermometer import OneWireTemperatureSensor, DS18S20, DS18B20, DS1822
from ..exceptions import OneWireException
from ..utils import *

__temperatureSensors = {
    0x10: DS18S20,
    0x22: DS1822,
    0x28: DS18B20,
}


def TemperatureSensor(bus, rom):
    # type: (UART_Adapter, str) -> OneWireTemperatureSensor
    family_code = iord(str2rom(rom), 0)
    if family_code not in __temperatureSensors:
        raise OneWireException("Unsupported family code: %d" % family_code)
    return __temperatureSensors[family_code](bus, rom=rom)

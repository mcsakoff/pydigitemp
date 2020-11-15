import warnings

from ..utils import *
from ..master import UART_Adapter

if PY3:
    from typing import List

__all__ = ['AddressableDevice']


class OneWireDevice(object):
    """
    Abstract 1-Wire device.
    """
    TYPES = {
        0x01: 'DS2401 - Silicon Serial Number',
        0x10: 'DS18S20 - High-precision Digital Thermometer',
        0x22: 'DS1822 - Econo Digital Thermometer',
        0x28: 'DS18B20 - Programmable Resolution Digital Thermometer',
    }

    def __init__(self, bus):
        # type: (UART_Adapter) -> None
        self.bus = bus

    @classmethod
    def _device_name(cls, family_code):
        # type: (int) -> str
        return OneWireDevice.TYPES.get(family_code, 'Unknown 1-Wire device')


#
# This class is deprecated and stays here only for backward compatibility.
# It will be removed eventually.
#
class AddressableDevice(OneWireDevice):

    def get_connected_ROMs(self):
        # type: () -> List[str]
        warnings.warn("deprecated", DeprecationWarning)
        return self.bus.get_connected_ROMs()

    def alarm_search(self):
        # type: () -> List[str]
        warnings.warn("deprecated", DeprecationWarning)
        return self.bus.alarm_search()

    def is_connected(self, rom_code):
        # type: (bytes) -> bool
        warnings.warn("deprecated", DeprecationWarning)
        return self.bus.is_connected(rom_code)

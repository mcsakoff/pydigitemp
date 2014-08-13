import time
import struct

from ..utils import *
from ..exceptions import OneWireException, CRCError, DeviceError
from .generic import AddressableDevice

__all__ = ['DS18S20', 'DS1820', 'DS1920']


class OneWireTemperatureSensor(AddressableDevice):
    """
    Abstract class for temperature sensors.
    """
    T_CONV = 0.750  # temperature conversion time, default value
    T_RW = 0.010    # eeprom write time, default value

    def __init__(self, bus, rom=None):
        """
        If no ROM code passed we suppose that thare is only one 1-wire device on the line!
        """
        AddressableDevice.__init__(self, bus)
        self.t_conv = self.T_CONV
        self.t_rw = self.T_RW
        if rom is None:  # only one 1-wire device connected
            self.single_mode = True
            self.rom_code = self._read_ROM()
            self.parasitic = self._power_supply()
        else:
            self.single_mode = False
            self.rom_code = str2rom(rom)
            if not self.is_connected(self.rom_code):
                raise DeviceError('Device with ROM code %s not found' % rom2str(self.rom_code))
            self._reset()
            self.parasitic = self._power_supply()

    @property
    def rom(self):
        """
        :return: ROM code in human readable format
        """
        return rom2str(self.rom_code)

    def info(self):
        print('Bus: %s' % self.bus.name)
        print('Device: %s' % self._device_name(self.rom_code))
        print('ROM Code: %s' % self.rom)
        print('Power Mode: %s' % ('parasitic' if self.parasitic else 'external'))
        print('Connection Mode: %s' % ('single-drop' if self.single_mode else 'multidrop'))

    def save_eeprom(self):
        self._copy_scratchpad()

    def load_eeprom(self):
        self._recall()

    def get_temperature(self, attempts=3):
        """
        Initiates a single temperature conversion then read scratchpad memory
        and caculate the temperature.

        :param precise: If True - calculate extended resolution temperature
        :param attempts: retry on CRC errors
        :return: float, temperature in Celcius
        """
        attempts = attempts if attempts > 1 else 1
        try:
            self._reset()
            self._convert_T()
            for i in range(attempts):
                self._reset()
                try:
                    scratchpad = self._read_scratchpad()
                    break
                except CRCError:
                    pass
            else:
                raise CRCError('read_scratchpad: CRC error')
            return self._calc_temperature(scratchpad)

        except OneWireException as e:
            print('Temperature sensor (%s) error %s' % (rom2str(self.rom_code), str(e)))
            return None

     # ---[ Function Commands ]----

    def _convert_T(self):
        """
        CONVERT T [44h]
        This command initiates a single temperature conversion.
        """
        self.bus.write_byte(0x44)
        self._wait(self.t_conv)

    def _read_scratchpad(self):
        """
        READ SCRATCHPAD [BEh]
        This command allows the master to read the contents of the scratchpad.
        """
        self.bus.write_byte(0xbe)
        raw = self.bus.read_bytes(8)
        crc = self.bus.read_byte()
        if crc8(raw) != crc:
            raise CRCError('read_scratchpad CRC error')
        return raw

    def _write_scratchpad(self, raw):
        """
        WRITE SCRATCHPAD [4Eh]
        This command allows the master to write data to the slave's scratchpad. Data must be transmitted least
        significant bit first and all bytes MUST be written before the master issues a reset.
        """
        self.bus.write_byte(0x4e)
        self.bus.write_bytes(raw)

    def _copy_scratchpad(self):
        """
        COPY SCRATCHPAD [48h]
        This command copies the contents of the scratchpad to EEPROM.
        """
        self.bus.write_byte(0x48)
        self._wait(self.t_rw)

    def _recall(self):
        """
        RECALL EE [B8h]
        This command recalls values from EEPROM and places the data in the scratchpad memory.
        """
        if not self.parasitic:
            self.bus.write_byte(0xb8)
            self._wait()

    def _power_supply(self):
        """
        READ POWER SUPPLY [B4h]
        The master device issues this command to determine if devices on the bus are using parasite power.

        :return: True if device is in parasitic mode
        """
        self.bus.write_byte(0xb4)
        # parasite powered will pull the bus low and we will get 0x0 on read
        return self.bus.read_bit() == 0b0

     # ---[ Helper Functions ]----

    def _reset(self):
        """
        Send reset pulse, wait for presence and then select the device.
        """
        if self.single_mode:
            self._skip_ROM()  # because it is single device
        else:
            self._match_ROM(self.rom_code)

    def _wait(self, sec=0.75):
        """
        Wait for specified time in parasitic mode or until operation is finished in external power mode.
        """
        if self.parasitic:
            time.sleep(sec)
        else:
            while self.bus.read_bit() == 0x0:
                pass

    def _calc_temperature(self, scratchpad):
        """
        Calculate temperature from scratchpad
        """
        raise NotImplementedError()


class DS18S20(OneWireTemperatureSensor):
    """
    Represents one DS18S20 (temperature sensor) connected to the 1-Wire bus.
    See: http://datasheets.maximintegrated.com/en/ds/DS18S20.pdf
    """

    def __init__(self, bus, rom=None):
        OneWireTemperatureSensor.__init__(self, bus, rom)
        family_code = iord(self.rom_code, 0)
        if family_code != 0x10:
            raise DeviceError('The device is not a DS1820/DS18S20/DS1920 Temperature Sensor')

    @classmethod
    def _calc_temperature(cls, scratchpad, precise=True):
        """
        Extract temerature value from scratchpad.

        :param scratchpad: Scratchpad 8-bytes as bytes.
        :return: float, temperature in Celcius
        """
        temperature = float(struct.unpack('<h', scratchpad[0:2])[0]) / 2.0
        if precise:
            count_remain = iord(scratchpad, 6)
            count_per_c = iord(scratchpad, 7)
            temperature = round(int(temperature) - 0.25 + 1.0 * (count_per_c - count_remain) / count_per_c, 2)
        return temperature

DS1820 = DS18S20
DS1920 = DS18S20

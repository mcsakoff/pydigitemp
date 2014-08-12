import time
from .utils import *
from .exceptions import OneWireException, CRCError, DeviceError

__all__ = ['OneWireDevice', 'DS18S20', 'DS1820', 'DS1920']


class OneWireDevice(object):
    """
    Abstract class with main functions for 1-Wire devices.
    See: http://www.maximintegrated.com/en/app-notes/index.mvp/id/937
    """
    TYPES = {
        0x10: 'DS1820 / DS18S20 / DS1920 - High-precision Digital Termometer',
    }

    def __init__(self, bus):
        self.bus = bus

    @classmethod
    def _device_name(cls, rom_code):
        return OneWireDevice.TYPES.get(iord(rom_code, 0), 'Unknown 1-Wire device')

    # ---[ Commands ]---

    def _read_ROM(self):
        self.bus.reset()
        self.bus.write_byte(0x33)
        rom_code = self.bus.read_bytes(8)
        crc = crc8(rom_code[0:7])
        if crc != iord(rom_code, 7):
            raise CRCError('read_ROM CRC error')
        return rom_code

    def _match_ROM(self, rom_code):
        self.bus.reset()
        self.bus.write_byte(0x55)
        self.bus.write_bytes(rom_code)

    def _skip_ROM(self):
        self.bus.reset()
        self.bus.write_byte(0xcc)

    # ---[ Functions ]---

    def _convert_T(self, parasite_mode):
        self.bus.write_byte(0x44)
        if parasite_mode:
            time.sleep(0.75)
        else:
            while self.bus.read_byte() == 0x0:
                time.sleep(0.0001)

    def _power_supply(self):
        """
        Return True if device is in parasitic mode
        """
        self.bus.write_byte(0xb4)
        # parasite powered will pull the bus low and we will get 0x0 on read
        return self.bus.read_bit() == 0b0

    def _read_scratchpad(self):
        self.bus.write_byte(0xbe)
        raw = self.bus.read_bytes(8)
        crc = self.bus.read_byte()
        if crc8(raw) != crc:
            raise CRCError('read_scratchpad CRC error')
        return raw

    # ---[ High-level Functions ]---

    def is_connected(self, rom_code):
        """
        Checking if a device with the ROM connected to the bus.
        Uses Search ROM command internally.
        """
        self.bus.reset()
        self.bus.write_byte(0xf0)
        for bit in rom2bits(rom_code):
            b1 = self.bus.read_bit()
            b2 = self.bus.read_bit()
            if b1 == b2 == 0b1:
                return False
            self.bus.write_bit(bit)
        return True

    # ---[ Helper Functions ]----

    def get_connected_ROMs(self, human_readable=False):
        """
        Get ROMs of all connected devices.
        """
        complete_roms = []
        partial_roms = []

        def search(current_rom=None):
            if current_rom is None:
                current_rom = []
            else:
                current_rom = current_rom[:]
            # send search command
            self.bus.reset()
            self.bus.write_byte(0xf0)
            # send known bits
            for bit in current_rom:
                self.bus.read_bit()  # skip bitN
                self.bus.read_bit()  # skip complement of bitN
                self.bus.write_bit(bit)
            # read rest of the bits
            for i in range(64 - len(current_rom)):
                b1 = self.bus.read_bit()
                b2 = self.bus.read_bit()
                if b1 != b2:  # all devices have this bit set to 0 or 1
                    current_rom.append(b1)
                    self.bus.write_bit(b1)
                elif b1 == b2 == 0b0:
                    # there are two or more devices on the bus with bit 0 and 1 in this position
                    # save version with 1 as possible rom ...
                    rom = current_rom[:]
                    rom.append(0b1)
                    partial_roms.append(rom)
                    # ... and proceed with 0
                    current_rom.append(0b0)
                    self.bus.write_bit(0b0)
                else:
                    raise OneWireException('Search command got wrong bits (two sequential 0b1)')
            complete_roms.append(bits2rom(current_rom))

        search()
        while len(partial_roms):
            search(partial_roms.pop())

        if human_readable:
            complete_roms = [rom2str(rom) for rom in complete_roms]

        return complete_roms


class DS18S20(OneWireDevice):
    """
    Represents one DS1820 (temperature sensor) connected to the 1-Wire bus.
    See: http://datasheets.maximintegrated.com/en/ds/DS18S20.pdf

    If no ROM code passed we suppose that thare is only one 1-wire device on the line!
    """
    def __init__(self, bus, rom=None, debug=False):
        OneWireDevice.__init__(self, bus)
        self.debug = debug
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

        family_code = iord(self.rom_code, 0)
        if family_code != 0x10:
            raise DeviceError('The device is not a DS1820 / DS18S20 / DS1920 Temperature Sensor')

    def info(self):
        print('Bus: %s' % self.bus.name)
        print('Device: %s' % self._device_name(self.rom_code))
        print('ROM Code: %s' % self.rom)
        print('Power Mode: %s' % ('parasitic' if self.parasitic else 'external'))
        print('Single Device: %s' % ('yes' if self.single_mode else 'no'))

    @property
    def rom(self):
        """
        :return: ROM code in human readable format
        """
        return rom2str(self.rom_code)

    def _reset(self):
        """
        Send reset pulse, wait for presence and then select the device.
        """
        if self.single_mode:
            self._skip_ROM()  # because it is single device
        else:
            self._match_ROM(self.rom_code)

    @classmethod
    def _calc_temperature(cls, scratchpad, precise=False):
        """
        Extract temerature value from scratchpad.

        :param scratchpad: Scratchpad 8-bytes as bytes.
        :param precise: If True - calculate extended resolution temperature
        :return: float, temperature in Celcius
        """
        temp_read = iord(scratchpad, 0)
        temp_sign = iord(scratchpad, 1)
        count_remain = iord(scratchpad, 6)
        count_per_c = iord(scratchpad, 7)

        if temp_sign == 0x00:
            temperature = temp_read / 2.0
        elif temp_sign == 0xff:
            temperature = - (0xff - temp_read + 1) / 2.0
        else:
            raise OneWireException('Temerature sign byte error: 0x%02x' % temp_sign)

        if precise:
            temperature = round(int(temperature) - 0.25 + 1.0 * (count_per_c - count_remain) / count_per_c, 2)

        return temperature

    def get_temperature(self, precise=False, attempts=3):
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
            self._convert_T(self.parasitic)
            for i in range(attempts):
                self._reset()
                try:
                    scratchpad = self._read_scratchpad()
                    break
                except CRCError:
                    pass
            else:
                raise CRCError('read_scratchpad: CRC error')
            return self._calc_temperature(scratchpad, precise=precise)

        except OneWireException as e:
            print('DS1820 sensor (%s) error %s' % (rom2str(self.rom_code), str(e)))
            return None

DS1820 = DS18S20
DS1920 = DS18S20

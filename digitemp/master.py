"""
Conceptual Overview
-------------------

Properly configured with respect to baud rate, data bits per character, parity and number of stop bits,
a 115,200 bit per second capable UART provides the input and output timing necessary to implement a 1-Wire master.
The UART produces the 1-Wire reset pulse, as well as read- and write-time slots. The microprocessor simply puts
one-byte character codes into the UART transmit register to send a 1-Wire 1 or 0 bit and the UART does the work.
Conversely, the microprocessor reads single-byte character codes corresponding to a 1 or 0 bit read from a 1-Wire device.
All 1-Wire bit transfers require the bus master, the UART, to begin the cycle by driving the 1-Wire bus low.
Therefore, each 1-Wire bit cycle includes a byte transmit and byte receive by the UART. When reading, the received data
is of interest, when writing, however, the receive byte is discarded. Depending on the UART's read and write first-in,
first-out (FIFO) buffer depth, the UART can also frame 1-Wire bits into byte values further reducing the processor
overhead.

For details see:
    Using an UART to Implement a 1-Wire Bus Master (http://www.maximintegrated.com/en/app-notes/index.mvp/id/214)
"""
import serial
import platform
from .utils import *
from .exceptions import DeviceError, AdapterError, CRCError

if PY3:
    from typing import Optional, List

if platform.system() == "Windows":
    def fcntl_flock():
        pass

    def fcntl_funlock():
        pass
else:
    import fcntl

    def fcntl_flock(fh):
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)

    def fcntl_funlock(fh):
        fcntl.flock(fh, fcntl.LOCK_UN)


class UART_Adapter(object):

    def __init__(self, port, timeout=3):
        # type: (str, Optional[float]) -> None
        self.locked = False
        try:
            self.uart = serial.Serial(port, timeout=timeout)
            self.uart.dtr = True
        except Exception as e:
            raise DeviceError(e)
        self._lock()

    @property
    def name(self):
        # type: () -> str
        return self.uart.name

    def close(self):
        # type: () -> None
        if self.uart.is_open:
            self._unlock()
            try:
                self.uart.dtr = False
                self.uart.close()
            except Exception as e:
                raise DeviceError(e)

    def _lock(self):
        # type: () -> None
        if self.uart.is_open:
            try:
                fcntl_flock(self.uart.fileno())
                self.locked = True
            except IOError:  # Already locked
                raise DeviceError('Cannot lock serial port: %s' % self.name)

    def _unlock(self):
        # type: () -> None
        """
        Un-lock serial port
        """
        if self.locked:
            try:
                fcntl_funlock(self.uart.fileno())
            except IOError:
                raise DeviceError('Cannot unlock serial port: %s' % self.name)
            self.locked = False

    def clear(self):
        # type: () -> None
        """
        Clear input and output buffers. Just in case.
        """
        try:
            self.uart.reset_input_buffer()
            self.uart.reset_output_buffer()
        except Exception as e:
            raise DeviceError(e)

    # ---[ Data Read/Write Methods ]----

    def read_bytes(self, size=1):
        # type: (int) -> bytes
        """
        Read N bytes from serial line.
        """
        data = []
        for i in range(size):
            data.append(self.read_byte())
        return bytesarray2bytes(data)

    def write_bytes(self, data):
        # type: (bytes) -> None
        """
        Write bytes to serial line.
        """
        for d in iterbytes(data):
            self.write_byte(d)

    def read_byte(self):
        # type: () -> int
        """
        Read one byte from serial line. Same as read_bit but for 8-bits.
        :return: integer 0x00..0xff
        """
        self.clear()
        try:
            self.uart.write(b'\xff\xff\xff\xff\xff\xff\xff\xff')
            data = self.uart.read(8)
        except Exception as e:
            raise DeviceError(e)
        if len(data) != 8:
            raise AdapterError('Read error')
        value = 0
        for b in reversed(list(iterbytes(data))):
            value <<= 1
            if b == 0xff:
                value += 1
        return value

    def write_byte(self, data):
        # type: (int) -> None
        """
        Write one byte to serial line. Same as write_bit but for 8-bits.
        :param data: integer 0x00..0xff
        """
        bits = []
        for i in range(8):
            bits.append(0xff if data % 2 else 0x00)  # 0 --> 0x00, 1 --> 0xff
            data >>= 1
        bits = bytesarray2bytes(bits)
        self.clear()
        try:
            self.uart.write(bits)
            back = self.uart.read(8)
        except Exception as e:
            raise DeviceError(e)
        if len(back) != 8:
            raise AdapterError('Write error')
        if bits != back:
            raise AdapterError('Noise on the line detected')

    def read_bit(self):
        # type: () -> int
        """
        Read one bit from serial line.

        Writing 0xff starts read time slot. If device wants to send 0x0 it will pull the bus low
        ad we will read back value < 0xff. Otherwise it is 0x1 was sent.

        :return: integer 0x0..0x1
        """
        self.clear()
        try:
            self.uart.write(b'\xff')
            b = self.uart.read(1)
        except Exception as e:
            raise DeviceError(e)
        if len(b) != 1:
            raise AdapterError('Read error')
        value = bord(b)
        return 0b1 if value == 0xff else 0b0

    def write_bit(self, bit):
        # type: (int) -> None
        """
        Write one bit to serial line.

        0xff - writes 0x1, 0x00 writes 0x0. Read-back value shall match the value we write.
        Otherwise someone else was writing to the bus at the same time.

        :param bit: integer 0x0..0x1
        """
        bit = b'\xff' if bit else b'\x00'
        self.clear()
        try:
            self.uart.write(bit)
            back = self.uart.read(1)
        except Exception as e:
            raise DeviceError(e)
        if len(back) != 1:
            raise AdapterError('Write error')
        if bit != back:
            raise AdapterError('Noise on the line detected')

    def reset(self):
        # type: () -> None
        """
        Reset and presence detect.
        """
        self.clear()
        try:
            self.uart.baudrate = 9600
            self.uart.write(b'\xf0')
            b = self.uart.read(1)
        except Exception as e:
            raise DeviceError(e)
        if len(b) != 1:
            raise AdapterError('Read/Write error')
        d = bord(b)
        try:
            self.uart.baudrate = 115200
        except Exception as e:
            raise DeviceError(e)
        if d == 0xf0:
            raise AdapterError('No 1-wire device present')
        elif 0x10 <= d <= 0xe0:
            return
        else:
            raise AdapterError('Presence error: 0x%02x' % d)

    # ---[ ROM Commands ]----

    def read_ROM(self):
        # type: () -> bytes
        """
        READ ROM [33h]

        This command can only be used when there is one device on the bus. It allows the bus driver to read the
        device's 64-bit ROM code without using the Search ROM procedure. If this command is used when there
        is more than one device present on the bus, a data collision will occur when all the devices attempt to
        respond at the same time.
        """
        self.reset()
        self.write_byte(0x33)
        rom_code = self.read_bytes(8)
        crc = crc8(rom_code[0:7])
        if crc != iord(rom_code, 7):
            raise CRCError('read_ROM CRC error')
        return rom_code

    def match_ROM(self, rom_code):
        # type: (bytes) -> None
        """
        MATCH ROM [55h]

        The match ROM command allows to address a specific device on a multidrop or single-drop bus.
        Only the device that exactly matches the 64-bit ROM code sequence will respond to the function command
        issued by the master; all other devices on the bus will wait for a reset pulse.
        """
        self.reset()
        self.write_byte(0x55)
        self.write_bytes(rom_code)

    def skip_ROM(self):
        # type: () -> None
        """
        The master can use this command to address all devices on the bus simultaneously without sending out
        any ROM code information.
        """
        self.reset()
        self.write_byte(0xcc)

    def search_ROM(self, alarm=False):
        # type: (bool) -> List[bytes]
        """
        SEARCH ROM [F0h]
        The master learns the ROM codes through a process of elimination that requires the master to perform
        a Search ROM cycle as many times as necessary to identify all of the devices.

        ALARM SEARCH [ECh]
        The operation of this command is identical to the operation of the Search ROM command except that
        only devices with a set alarm flag will respond.
        """
        complete_roms = []
        partial_roms = []

        def search(current_rom=None):
            if current_rom is None:
                current_rom = []
            else:
                current_rom = current_rom[:]
            # send search command
            self.reset()
            self.write_byte(0xec if alarm else 0xf0)
            # send known bits
            for bit in current_rom:
                self.read_bit()  # skip bitN
                self.read_bit()  # skip complement of bitN
                self.write_bit(bit)
            # read rest of the bits
            for i in range(64 - len(current_rom)):
                b1 = self.read_bit()
                b2 = self.read_bit()
                if b1 != b2:  # all devices have this bit set to 0 or 1
                    current_rom.append(b1)
                    self.write_bit(b1)
                elif b1 == b2 == 0b0:
                    # there are two or more devices on the bus with bit 0 and 1 in this position
                    # save version with 1 as possible rom ...
                    rom = current_rom[:]
                    rom.append(0b1)
                    partial_roms.append(rom)
                    # ... and proceed with 0
                    current_rom.append(0b0)
                    self.write_bit(0b0)
                else:  # b1 == b2 == 1:
                    if alarm:
                        # In alarm search that means there is no more alarming devices
                        return
                    else:
                        raise AdapterError('Search command got wrong bits (two sequential 0b1)')
            complete_roms.append(bits2rom(current_rom))

        search()
        while len(partial_roms):
            search(partial_roms.pop())

        return complete_roms

    # ---[ Helper Functions ]----

    def get_connected_ROMs(self):
        # type: () -> List[str]
        roms = self.search_ROM(alarm=False)
        return [rom2str(rom) for rom in roms]

    def alarm_search(self):
        # type: () -> List[str]
        roms = self.search_ROM(alarm=True)
        return [rom2str(rom) for rom in roms]

    def is_connected(self, rom_code):
        # type: (bytes) -> bool
        """
        :return: True if a device with the ROM connected to the bus.
        """
        self.reset()
        self.write_byte(0xf0)
        for bit in rom2bits(rom_code):
            b1 = self.read_bit()
            b2 = self.read_bit()
            if b1 == b2 == 0b1:
                return False
            self.write_bit(bit)
        return True

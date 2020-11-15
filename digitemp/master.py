"""
Conceptual Overview
-------------------

Properly configured with respect to baud rate, data bits per character, parity and number of stop bits,
a 115,200 bit per second capable UART provides the input and output timing necessary to implement a 1-Wire master.
The UART produces the 1-Wire reset pulse, as well as read- and write-time slots. The microprocessor simply puts
one-byte character codes into the UART transmit register to send a 1-Wire 1 or 0 bit and the UART does the work.
Conversely, the microprocessor reads single-byte character codes corresponding to a 1 or 0 bit read from a 1-Wire slave.
All 1-Wire bit transfers require the bus master, the UART, to begin the cycle by driving the 1-Wire bus low.
Therefore, each 1-Wire bit cycle includes a byte transmit and byte receive by the UART. When reading, the received data
is of interest, when writing, however, the receive byte is discarded. Depending on the UART's read and write first-in,
first-out (FIFO) buffer depth, the UART can also frame 1-Wire bits into byte values further reducing the processor
overhead.

For details see:
    Using an UART to Implement a 1-Wire Bus Master (http://www.maximintegrated.com/en/app-notes/index.mvp/id/214)
"""

import serial
import fcntl

from .utils import *
from .exceptions import DeviceError, AdapterError


class UART_Adapter(object):

    def __init__(self, port, timeout=3):
        self.locked = False
        try:
            self.uart = serial.Serial(port, timeout=timeout)
            self.uart.dtr = True
        except Exception as e:
            raise DeviceError(e)
        self._lock()

    @property
    def name(self):
        return self.uart.name

    def close(self):
        if self.uart.is_open:
            self._unlock()
            try:
                self.uart.dtr = False
                self.uart.close()
            except Exception as e:
                raise DeviceError(e)

    def _lock(self):
        if self.uart.is_open:
            try:
                fcntl.flock(self.uart.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                self.locked = True
            except IOError:  # Already locked
                raise DeviceError('Cannot lock serial port: %s' % self.name)

    def _unlock(self):
        """
        Un-lock serial port
        """
        if self.locked:
            try:
                fcntl.flock(self.uart.fileno(), fcntl.LOCK_UN)
            except IOError:
                raise DeviceError('Cannot unlock serial port: %s' % self.name)
            self.locked = False

    def clear(self):
        """
        Clear input and output buffers. Just in case.
        """
        try:
            self.uart.reset_input_buffer()
            self.uart.reset_output_buffer()
        except Exception as e:
            raise DeviceError(e)

    def read_bytes(self, size=1):
        """
        Read N bytes from serial line.
        :param size: integer
        :return: bytes
        """
        data = []
        for i in range(size):
            data.append(self.read_byte())
        return bytesarray2bytes(data)

    def write_bytes(self, data):
        """
        Write bytes to serial line.
        :param data: bytes
        """
        for d in iterbytes(data):
            self.write_byte(d)

    def read_byte(self):
        """
        Read one byte from serial line. Same as read_bit but for 8-bits.
        :return: integer 0x00..0xff
        """
        self.clear()
        try:
            self.uart.write(b'\xff\xff\xff\xff\xff\xff\xff\xff')
            data = self.uart.read(8)
        except Exception as e:
            return DeviceError(e)
        if len(data) != 8:
            raise AdapterError('Read error')
        value = 0
        for b in reversed(list(iterbytes(data))):
            value <<= 1
            if b == 0xff:
                value += 1
        return value

    def write_byte(self, data):
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
            return DeviceError(e)
        if len(back) != 8:
            raise AdapterError('Write error')
        if bits != back:
            raise AdapterError('Noise on the line detected')

    def read_bit(self):
        """
        Read one bit from serial line.

        Writing 0xff starts read time slot. If slave wants to send 0x0 it will pull the bus low
        ad we will read back value < 0xff. Otherwise it is 0x1 was sent.

        :return: integer 0x0..0x1
        """
        self.clear()
        try:
            self.uart.write(b'\xff')
            b = self.uart.read(1)
        except Exception as e:
            return DeviceError(e)
        if len(b) != 1:
            raise AdapterError('Read error')
        value = bord(b)
        return 0b1 if value == 0xff else 0b0

    def write_bit(self, bit):
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
            return DeviceError(e)
        if len(back) != 1:
            raise AdapterError('Write error')
        if bit != back:
            raise AdapterError('Noise on the line detected')

    def reset(self):
        """
        Reset and presence detect.
        """
        self.clear()
        try:
            self.uart.baudrate = 9600
            self.uart.write(b'\xf0')
            b = self.uart.read(1)
        except Exception as e:
            return DeviceError(e)
        if len(b) != 1:
            raise AdapterError('Read/Write error')
        d = bord(b)
        try:
            self.uart.baudrate = 115200
        except Exception as e:
            return DeviceError(e)
        if d == 0xf0:
            raise AdapterError('No 1-wire device present')
        elif 0x10 <= d <= 0xe0:
            return
        else:
            raise AdapterError('Presence error: 0x%02x' % d)

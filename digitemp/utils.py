import sys

__all__ = ['bytesarray2bytes', 'iterbytes', 'bord', 'iord', 'crc8',
           'rom2str', 'str2rom', 'rom2bits', 'bits2rom', 'PY3']

PY3 = sys.version_info[0] == 3

if PY3:
    from typing import List, Iterator

    def bytesarray2bytes(array):                                # [110, 116, 112]     => b'ntp'
        # type: (List[int]) -> bytes
        return bytes(array)

    iterbytes = iter                                            # b'ntp'              => iter([110, 116, 112])

    def bord(buf):                                              # b'\x01'             => 0x01
        # type: (bytes) -> int
        return buf[0]

    def iord(buf, i):                                           # b'\x05\x06\x07', 1  => 0x06
        # type: (bytes, int) -> int
        return buf[i]

    def fromhex(s):
        # type: (str) -> bytes
        return bytes.fromhex(s)

else:
    def bytesarray2bytes(array):                                # [110, 116, 112]     => b'ntp'
        # type: (List[int]) -> bytes
        return b''.join(map(chr, array))

    def iterbytes(buf):                                         # b'ntp'              => iter([110, 116, 112])
        # type: (bytes) -> Iterator[int]
        return map(ord, buf)

    bord = ord                                                  # b'\x01'             => 0x01

    def iord(buf, i):                                           # b'\x05\x06\x07', 1  => 0x06
        # type: (bytes, int) -> int
        return ord(buf[i])

    def fromhex(s):
        # type: (str) -> bytes
        return s.decode('hex')


def crc8(data):
    # type: (bytes) -> int
    crc = 0x00
    for byte in iterbytes(data):
        for i in range(8):
            mix = (crc ^ byte) & 0x01
            crc >>= 1
            if mix:
                crc ^= 0x8c
            byte >>= 1
    return crc


def rom2str(rom_code):
    # type: (bytes) -> str
    return ''.join('%02X' % i for i in iterbytes(rom_code))


def str2rom(string):
    # type: (str) -> bytes
    return fromhex(string)


def rom2bits(rom_code):
    # type: (bytes) -> List[int]
    if len(rom_code) != 8:
        raise ValueError('bytes array length shall be 8')
    bits = []
    for byte in iterbytes(rom_code):
        for n in range(8):
            bits.append(byte % 2)
            byte >>= 1
    return bits


def bits2rom(bits):
    # type: (List[int]) -> bytes
    if len(bits) != 64:
        raise ValueError('bits array length shall be 64')
    bytes_ = []
    for n in range(0, 64, 8):
        value = 0
        for b in reversed(bits[n:n+8]):
            value <<= 1
            value += 1 if b else 0
        bytes_.append(value)
    return bytesarray2bytes(bytes_)

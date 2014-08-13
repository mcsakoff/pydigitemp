import unittest

from digitemp.utils import crc8, rom2str, str2rom, rom2bits, bits2rom,\
    bytesarray2bytes, iterbytes, bord, iord


class UtilsTestCase(unittest.TestCase):

    def test_crc8(self):
        self.assertEqual(crc8(b'\x10\xa7\x5c\xa8\x02\x08\x00'), 0x1a)
        self.assertEqual(crc8(b'\x10\xa7\x5c\xa8\x02\x08\x00\x1a'), 0x00)

    def test_rom2str(self):
        self.assertEqual(rom2str(b'\x10\xa7\x5c\xa8\x02\x08\x00\x1a'), '10A75CA80208001A')

    def test_str2rom(self):
        self.assertEqual(str2rom('10A75CA80208001A'), b'\x10\xa7\x5c\xa8\x02\x08\x00\x1a')

    def test_rom2bits(self):
        self.assertEqual(rom2bits(b'\x01\x23\x45\x67\x89\xab\xcd\xef'),
                         [1, 0, 0, 0,   0, 0, 0, 0,
                          1, 1, 0, 0,   0, 1, 0, 0,
                          1, 0, 1, 0,   0, 0, 1, 0,
                          1, 1, 1, 0,   0, 1, 1, 0,
                          1, 0, 0, 1,   0, 0, 0, 1,
                          1, 1, 0, 1,   0, 1, 0, 1,
                          1, 0, 1, 1,   0, 0, 1, 1,
                          1, 1, 1, 1,   0, 1, 1, 1])

    def test_bits2rom(self):
        self.assertEqual(bits2rom([
                0, 0, 0, 0,    1, 0, 0, 0,
                0, 1, 0, 0,    1, 1, 0, 0,
                0, 0, 1, 0,    1, 0, 1, 0,
                0, 1, 1, 0,    1, 1, 1, 0,
                0, 0, 0, 1,    1, 0, 0, 1,
                0, 1, 0, 1,    1, 1, 0, 1,
                0, 0, 1, 1,    1, 0, 1, 1,
                0, 1, 1, 1,    1, 1, 1, 1,
            ]),
            b'\x10\x32\x54\x76\x98\xba\xdc\xfe'
        )

    def test_bytesarray2bytes(self):
        self.assertEqual(bytesarray2bytes([0x00, 0x55, 0xff]), b'\x00\x55\xff')

    def test_iterbytes(self):
        self.assertEqual(list(iterbytes(b'\x00\x55\xff')), [0x00, 0x55, 0xff])

    def test_bord(self):
        self.assertEqual(bord(b'\x01'), 0x01)
        self.assertEqual(bord(b'\xff'), 0xff)

    def test_iord(self):
        self.assertEqual(iord(b'\x05\x06\x07', 1), 0x06)

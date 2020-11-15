import unittest

from digitemp.device.thermometer import DS18S20, DS18B20


class DS18S20_TestCase(unittest.TestCase):
    DEFAULT_SCRATCHPAD = b'\xaa\x00\x4b\x46\xff\xff\x0c\x10'

    def test_01_temperature(self):
        def conv(temp_register):
            scratchpad = bytearray(self.DEFAULT_SCRATCHPAD)
            scratchpad[0] = temp_register & 0xff            # LSB
            scratchpad[1] = (temp_register >> 8) & 0xff     # MSB
            scratchpad = bytes(scratchpad)
            return DS18S20._s_calc_temperature(scratchpad, precise=False)

        self.assertEqual(conv(0x00aa), 85.0)
        self.assertEqual(conv(0x0032), 25.0)
        self.assertEqual(conv(0x0001), 0.5)
        self.assertEqual(conv(0x0000), 0.0)
        self.assertEqual(conv(0xffff), -0.5)
        self.assertEqual(conv(0xffce), -25.0)
        self.assertEqual(conv(0xff92), -55.0)


class DS18B20_TestCase(unittest.TestCase):
    DEFAULT_SCRATCHPAD = b'\x50\x05\x4b\x46\x7f\xff\x0c\x10'

    def test_01_temperature(self):
        def conv(temp_register):
            scratchpad = bytearray(self.DEFAULT_SCRATCHPAD)
            scratchpad[0] = temp_register & 0xff            # LSB
            scratchpad[1] = (temp_register >> 8) & 0xff     # MSB
            scratchpad = bytes(scratchpad)
            return DS18B20._calc_temperature(scratchpad)

        self.assertEqual(conv(0x07d0), 125.0)
        self.assertEqual(conv(0x0550), 85.0)
        self.assertEqual(conv(0x0191), 25.0625)
        self.assertEqual(conv(0x00a2), 10.125)
        self.assertEqual(conv(0x0008), 0.5)
        self.assertEqual(conv(0x0000), 0.0)
        self.assertEqual(conv(0xfff8), -0.5)
        self.assertEqual(conv(0xff5e), -10.125)
        self.assertEqual(conv(0xfe6f), -25.0625)
        self.assertEqual(conv(0xfc90), -55.0)

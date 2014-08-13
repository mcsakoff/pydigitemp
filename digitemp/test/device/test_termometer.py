import unittest

from digitemp.device.termometer import DS18S20


class DS18S20_TestCase(unittest.TestCase):
    DEFAULT_SCRATCHPAD = b'\xaa\x00\x4b\x46\xff\xff\x0c\x10'

    def test_01_temperature(self):
        def conv(temp_register):
            scratchpad = bytearray(self.DEFAULT_SCRATCHPAD)
            scratchpad[0] = temp_register & 0xff            # LSB
            scratchpad[1] = (temp_register >> 8) & 0xff     # MSB
            return DS18S20._calc_temperature(scratchpad, precise=False)

        self.assertEqual(conv(0x00aa), 85.0)
        self.assertEqual(conv(0x0032), 25.0)
        self.assertEqual(conv(0x0001), 0.5)
        self.assertEqual(conv(0x0000), 0.0)
        self.assertEqual(conv(0xffff), -0.5)
        self.assertEqual(conv(0xffce), -25.0)
        self.assertEqual(conv(0xff92), -55.0)

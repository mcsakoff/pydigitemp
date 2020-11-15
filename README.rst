==========
PyDigiTemp
==========

Python implementation of 1-Wire protocol.

Originally written to replace `digitemp <https://www.digitemp.com/>`_ utility in my pet project
and get direct access to 1-wire devices. It was created for reading DS1820 temperature sensor connected
to RS232 serial port through DS9097 adapter.

Documentation used
==================

* `Using an UART to Implement a 1-Wire Bus Master <http://www.maximintegrated.com/en/app-notes/index.mvp/id/214>`_
* `Book of iButton® Standards <http://pdfserv.maximintegrated.com/en/an/AN937.pdf>`_ (PDF)
* `DS18S20 High-Precision 1-Wire Digital Thermometer <http://datasheets.maximintegrated.com/en/ds/DS18S20.pdf>`_ (PDF)

Supported Hardware
==================

Master
------

* `DS9097 <http://www.maximintegrated.com/en/products/comms/ibutton/DS9097.html>`_ - COM port adapter which performs RS-232C level conversion.
* Custom 1-wire serial port interface (see below).

Slave
-----

* `DS1820 / DS18S20 / DS1920 <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS18S20.html>`_ - High-Precision Temperature Sensor.
* `DS18B20 <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS18B20.html>`_ - Programmable Resolution Temperature Sensor.
* `DS1822 <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS1822.html>`_ - Econo Temperature Sensor.

Usage
=====

Find ROM codes for all connected devices::

  from digitemp.master import UART_Adapter
  from digitemp.device import AddressableDevice

  print(AddressableDevice(UART_Adapter('/dev/ttyS0')).get_connected_ROMs())
  # ['108739A80208006F', '10A75CA80208001A']

Get temperature::

  from digitemp.master import UART_Adapter
  from digitemp.device import DS1820

  bus = UART_Adapter('/dev/ttyS0')  # DS9097 connected to COM1

  # only one 1-wire device on the bus:
  sensor = DS1820(bus)

  # specify device's ROM code if more than one 1-wire device on the bus:
  sensor = DS1820(bus, rom='10D67E5B02080037')

  # display sensor's information
  sensor.info()

  # get temperature
  print(sensor.get_temperature())
  # 25.48

Set resolution for DS18B20 and DS1822)::

  from digitemp.device import DS18B20
  sensor = DS18B20(bus)

  sensor.set_resolution(DS18B20.RES_9_BIT)

See more examples in *examples* directory.

`digitemp.device` module provides following classes:

* `DS18S20` - for DS1820, DS18S20 and DS1920 High-Precision Temperature Sensors (family code: `0x10`);
* `DS18B20` - for DS18B20 Programmable Resolution Temperature Sensors (family code: `0x28`);
* `DS1822` - for DS1822 Econo Temperature Sensor (family code: `0x22`)
* `DS1820`, `DS1920` - are aliases for `DS18S20`

Schematics
==========

IMPORTANT DISCLAIMER: All circuits presented here are collected from different sources on the Internet and thus are
provided on an entirely "as-is and no guarantees" basis. We do not provide a warranty of any kind and cannot be held
responsible in any manner.

1-wire serial port interface
----------------------------

See `Serial Port Temperature Sensors - Hardware Interface <http://martybugs.net/electronics/tempsensor/hardware.cgi>`_
for details.

USB/UART adapter
----------------

These are tested:

* `ds18b20-uart.svg <docs/ds18b20-uart.svg>`_
* `ds18b20-uart-par.svg <docs/ds18b20-uart-par.svg>`_
* `ds18b20-uart-dioda.svg <docs/ds18b20-uart-dioda.svg>`_
* `ds18b20-uart-diodapar.svg <docs/ds18b20-uart-diodapar.svg>`_

Not all schematics work in all cases, depending on adapter and cable length.

These are not tested yet:

* `ds18b20-uart-mosfet.svg <docs/ds18b20-uart-mosfet.svg>`_
* `ds18b20-uart-npn.svg <docs/ds18b20-uart-npn.svg>`_

Thanks
======

* `Slavko <https://github.com/slavkoja>`_ for SVG schematics and testing.

License
=======

Python license. In short, you can use this product in commercial and non-commercial applications,
modify it, redistribute it. A notification to the author when you use and/or modify it is welcome.

See the LICENSE file for the actual text of the license.

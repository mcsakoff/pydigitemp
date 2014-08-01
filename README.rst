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

Slave
-----

  * `DS1820 / DS18S20 / DS1920 <http://www.maximintegrated.com/en/products/analog/sensors-and-sensor-interface/DS18S20.html>`_ - Temperature Sensor.

Usage
=====

::

  from digitemp.master import UART_Adapter
  from digitemp.device import DS1820, OneWireDevice

  bus = UART_Adapter(0)  # DS9097 connected to COM1 (/dev/ttyS0)

  # only one 1-wire device on the bus:
  sensor = DS1820(bus)

  # specify device's ROM code if more than one 1-wire device on the bus:
  sensor = DS1820(bus, rom='10D67E5B02080037')

  # display sensor's information
  sensor.info()

  # get temperature
  t = sensor.getTemperature()                 # 25.5
  t = sensor.getTemperature(precise=True)     # 25.48

  # find ROM codes for all connected devices:
  print(OneWireDevice(bus).get_connected_ROMs(human_readable=True))

License
=======

Python license. In short, you can use this product in commercial and non-commercial applications,
modify it, redistribute it. A notification to the author when you use and/or modify it is welcome.

See the LICENSE file for the actual text of the license.

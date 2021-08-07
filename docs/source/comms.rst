Communications
==============

Reading from UART
-----------------

This will return one line of available data from the specified UART channel, if available.

.. code-block:: python
	
  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  uart_channel = 0

  data = fixture.uart_rx(channel, block=True, timeout=1)
  print(f"Data: {data})

Note: you can also have UART data printed directly to the console when received without calling uart_rx by using ``fixture = LagerFixture(print_uart=True)``


Writing to UART
---------------

This will write arbitrary strings to the specified UART channel. Note: at the present time, baud rate must be configured in firmware.

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  uart_channel = 0

  fixture.uart_tx(channel, "Hello, world!")


Transferring data from/to SPI
-----------------------------

This will write arbitrary data to the specified SPI channel and return an equal number of bytes read from the peripheral. Note: at the present time, SPI speed and mode must be configured in firmware.

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  spi_channel = 0
  chip_select_pin = 5
  data = "hello"

  data = fixture.spi_xfer(spi_channel, chip_select_pin, data)
  print(f"SPI Received: {data}")


Reading from I2C
----------------

This will read a specified number of bytes from a target I2C device connected to a specified I2C channel.

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  i2c_channel = 0
  target_address = 0x40
  bytes = 2

  data = fixture.i2c_rx(i2c_channel, target_address, bytes)
  print(f"I2C Received: {data}")

Writing to I2C
--------------

This will write arbitrary data to a target device connected to the specified I2C channel.

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  i2c_channel = 0
  target_address = 0x40
  data = "hello"

  fixture.i2c_tx(i2c_channel, target_address, data)
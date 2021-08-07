Basic GPIO
==========

Reading Input Pins
------------------

.. code-block:: python
	
  from lager_fixture import LagerFixture, INPUT

  fixture = LagerFixture()
  pin = 1

  fixture.set_gpio_mode(pin, INPUT)
  state = fixture.get_gpio(pin)

Setting Output Pins
-------------------

.. code-block:: python
  
  from lager_fixture import LagerFixture, OUTPUT, HIGH, LOW

  fixture = LagerFixture()
  pin = 1

  fixture.set_gpio_mode(pin, OUTPUT)
  state = fixture.set_gpio(pin, HIGH)
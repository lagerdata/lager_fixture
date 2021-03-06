Frequencies / PWM
=================

Reading a frequency input
-------------------------

Returns the frequency and duty cycle of a PWM signal being sent to a specified PWM input. Note: at the present time, the PWM channels must be configured in firmware.

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  pwm_channel = 0

  frequency, duty_cycle = fixture.get_freq(pwm_channel)
  print(f"Frequency is {frequency} Hz, Duty Cycle is {duty_cycle}%")


Outputting a PWM signal
-----------------------

Outputs a PWM signal on a specified channel, at the specified frequency and duty cycle (0-100).

.. code-block:: python

  from lager_fixture import LagerFixture

  fixture = LagerFixture()
  pwm_channel = 0
  frequency = 100 # Hz
  duty_cycle = 50 # Percent

  fixture.set_freq(pwm_channel, frequency, duty_cycle)
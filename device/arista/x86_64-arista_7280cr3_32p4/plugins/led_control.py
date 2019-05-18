#!/usr/bin/env python

try:
   import arista.utils.sonic_leds as arista_leds
except ImportError as e:
   raise ImportError("%s - required module not found" % str(e))

LedControl = arista_leds.getLedControl()

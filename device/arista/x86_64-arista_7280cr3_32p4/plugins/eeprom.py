#!/usr/bin/env python

try:
   import arista.utils.sonic_eeprom as arista_eeprom
except ImportError as e:
   raise ImportError("%s - required module not found" % str(e))

board = arista_eeprom.getTlvInfoDecoder()

#!/usr/bin/env python

try:
   import arista.utils.sonic_sfputil as arista_sfputil
except ImportError as e:
   raise ImportError("%s - required module not found" % str(e))

SfpUtil = arista_sfputil.getSfpUtil()

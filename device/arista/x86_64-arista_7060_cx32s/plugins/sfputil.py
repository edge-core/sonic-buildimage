#!/usr/bin/env python

try:
    import arista.utils.sonic_sfputil as arista_sfputil
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


sfputil = arista_sfputil.getSfpUtil()

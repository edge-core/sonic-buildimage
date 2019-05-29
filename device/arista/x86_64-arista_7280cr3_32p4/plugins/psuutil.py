# psuutil.py

try:
    import arista.utils.sonic_psu as arista_psuutil
except ImportError as e:
    raise ImportError("%s - required module not found" % str(e))

PsuUtil = arista_psuutil.getPsuUtil()

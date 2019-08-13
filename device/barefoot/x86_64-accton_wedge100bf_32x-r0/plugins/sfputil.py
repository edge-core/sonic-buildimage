#!/usr/bin/env python

try:
    import os
    import sys
    import importlib
    import time

    sys.path.append(os.path.dirname(__file__))
    import pltfm_mgr_rpc
    from pltfm_mgr_rpc.ttypes import *

    from thrift.transport import TSocket
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol
    from thrift.protocol import TMultiplexedProtocol

    from sonic_sfp.sfputilbase import SfpUtilBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

thrift_server = 'localhost'
transport = None
pltfm_mgr = None

SFP_EEPROM_CACHE = "/var/run/platform/sfp/cache"

class SfpUtil(SfpUtilBase):
    """Platform-specific SfpUtil class"""

    PORT_START = 1
    PORT_END = 0
    PORTS_IN_BLOCK = 0
    QSFP_PORT_START = 1
    QSFP_PORT_END = 0
    EEPROM_OFFSET = 0

    @property
    def port_start(self):
        self.update_port_info()
        return self.PORT_START

    @property
    def port_end(self):
        self.update_port_info()
        return self.PORT_END

    @property
    def qsfp_ports(self):
        self.update_port_info()
        return range(self.QSFP_PORT_START, self.PORTS_IN_BLOCK + 1)

    @property
    def port_to_eeprom_mapping(self):
        print "dependency on sysfs has been removed"
        raise Exception() 

    def __init__(self):
        if not os.path.exists(os.path.dirname(SFP_EEPROM_CACHE)):
            try:
                os.makedirs(os.path.dirname(SFP_EEPROM_CACHE))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        open(SFP_EEPROM_CACHE, 'ab').close()

        SfpUtilBase.__init__(self)

    def update_port_info(self):
        global pltfm_mgr

        if self.QSFP_PORT_END == 0:
            self.thrift_setup()
            self.QSFP_PORT_END = pltfm_mgr.pltfm_mgr_qsfp_get_max_port();
            self.PORT_END = self.QSFP_PORT_END
            self.PORTS_IN_BLOCK = self.QSFP_PORT_END
            self.thrift_teardown()

    def thrift_setup(self):
        global thrift_server, transport, pltfm_mgr
        transport = TSocket.TSocket(thrift_server, 9090)

        transport = TTransport.TBufferedTransport(transport)
        bprotocol = TBinaryProtocol.TBinaryProtocol(transport)

        pltfm_mgr_client_module = importlib.import_module(".".join(["pltfm_mgr_rpc", "pltfm_mgr_rpc"]))
        pltfm_mgr_protocol = TMultiplexedProtocol.TMultiplexedProtocol(bprotocol, "pltfm_mgr_rpc")
        pltfm_mgr = pltfm_mgr_client_module.Client(pltfm_mgr_protocol)

        transport.open()

    def thrift_teardown(self):
        global transport
        transport.close()

    def get_presence(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        presence = False

        try:
            self.thrift_setup()
            presence = pltfm_mgr.pltfm_mgr_qsfp_presence_get(port_num)
            self.thrift_teardown()
        except Exception as e:
            print e.__doc__
            print e.message

        return presence

    def get_low_power_mode(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        self.thrift_setup()
        lpmode = pltfm_mgr.pltfm_mgr_qsfp_lpmode_get(port_num)
        self.thrift_teardown()
        return lpmode

    def set_low_power_mode(self, port_num, lpmode):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        self.thrift_setup()
        status = pltfm_mgr.pltfm_mgr_qsfp_lpmode_set(port_num, lpmode)
        self.thrift_teardown()
        return status

    def reset(self, port_num):
        # Check for invalid port_num
        if port_num < self.port_start or port_num > self.port_end:
            return False

        self.thrift_setup()
        status = pltfm_mgr.pltfm_mgr_qsfp_reset(port_num, True)
        status = pltfm_mgr.pltfm_mgr_qsfp_reset(port_num, False)
        self.thrift_teardown()
        return status

    def get_transceiver_change_event(self, timeout=0):
        phy_port_dict = {}
        status = True
        # TODO: Process transceiver plug-in/out event
        time.sleep(1)
        return status, phy_port_dict

    def _get_port_eeprom_path(self, port_num, devid):
        eeprom_path = None

        self.thrift_setup()
        presence = pltfm_mgr.pltfm_mgr_qsfp_presence_get(port_num)
        if presence == True:
            eeprom_cache = open(SFP_EEPROM_CACHE, 'wb')
            eeprom_hex = pltfm_mgr.pltfm_mgr_qsfp_info_get(port_num)
            eeprom_raw = bytearray.fromhex(eeprom_hex)
            eeprom_cache.write(eeprom_raw)
            eeprom_cache.close()
            eeprom_path = SFP_EEPROM_CACHE
        self.thrift_teardown()

        return eeprom_path


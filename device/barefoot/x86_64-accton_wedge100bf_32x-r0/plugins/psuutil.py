#!/usr/bin/env python

try:
    import os
    import sys
    import importlib

    sys.path.append(os.path.dirname(__file__))
    import pltfm_mgr_rpc
    from pltfm_mgr_rpc.ttypes import *

    from thrift.transport import TSocket
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol
    from thrift.protocol import TMultiplexedProtocol

    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

thrift_server = 'localhost'
transport = None
pltfm_mgr = None

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)

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

    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
        """
        return 2

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is faulty
        """
        if index is None:
            return False

        global pltfm_mgr

        try:
           self.thrift_setup()
           psu_info = pltfm_mgr.pltfm_mgr_pwr_supply_info_get(index)
           self.thrift_teardown()
        except:
            return False

        return (psu_info.ffault == False)

    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based index <index>
        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        if index is None:
            return False

        global pltfm_mgr

        try:
	    self.thrift_setup()
	    status = pltfm_mgr.pltfm_mgr_pwr_supply_present_get(index)
	    self.thrift_teardown()
        except:
            return False

        return status


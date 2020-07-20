#!/usr/bin/python


try:
    import importlib
    import time
    import os
    import re
    import sys
    import errno
    import datetime
    import logging
    import logging.config
    import yaml

    sys.path.append(os.path.dirname(__file__))
    import pltfm_mgr_rpc
    from pltfm_mgr_rpc.ttypes import *

    from thrift.transport import TSocket
    from thrift.transport import TTransport
    from thrift.protocol import TBinaryProtocol
    from thrift.protocol import TMultiplexedProtocol

    from argparse import ArgumentParser
    from cStringIO import StringIO
    from sonic_eeprom import eeprom_base
    from sonic_eeprom import eeprom_tlvinfo
except ImportError, e:
    raise ImportError (str(e) + "- required module not found")


eeprom_default_dict = {
	"prod_name"         : ("Product Name",                "0x21", 12),
	"odm_pcba_part_num" : ("Part Number",                 "0x22", 13),
	"prod_ser_num"      : ("Serial Number",               "0x23", 12),
	"ext_mac_addr"      : ("Extended MAC Address Base",   "0x24", 12),
	"sys_mfg_date"      : ("System Manufacturing Date",   "0x25",  4),
	"prod_ver"          : ("Product Version",             "0x26",  1),
	"ext_mac_addr_size" : ("Extende MAC Address Size",    "0x2A",  2),
	"sys_mfger"         : ("Manufacturer",                "0x2B",  8)
}

eeprom_dict = { "version"           : ("Version",                     None,    0),
		"pcb_mfger"         : ("PCB Manufacturer",            "0x01",  8),
		"prod_ser_num"      : ("Serial Number",               "0x23", 12),
		"bfn_pcba_part_num" : ("Switch PCBA Part Number",     "0x02", 12),
		"odm_pcba_part_num" : ("Part Number",                 "0x22", 13),
		"bfn_pcbb_part_num" : ("Switch PCBB Part Number",     "0x04", 12),
		"sys_asm_part_num"  : ("System Assembly Part Number", "0x05", 12),
		"prod_state"        : ("Product Production State",    "0x06",  1),
		"location"          : ("EEPROM Location of Fabric",   "0x07",  8),
		"ext_mac_addr_size" : ("Extende MAC Address Size",    "0x08",  2),
		"sys_mfg_date"      : ("System Manufacturing Date",   "0x25",  4),
		"prod_name"         : ("Product Name",                "0x21", 12),
		"prod_ver"          : ("Product Version",             "0x26",  1),
		"prod_part_num"     : ("Product Part Number",         "0x09",  8),
		"sys_mfger"         : ("Manufacturer",                "0x2B",  8),
		"assembled_at"      : ("Assembled at",                "0x08",  8),
		"prod_ast_tag"      : ("Product Asset Tag",           "0x09", 12),
		"loc_mac_addr"      : ("Local MAC address",           "0x0A", 12),
		"odm_pcba_ser_num"  : ("ODM PBCA Serial Number",      "0x0B", 12),
		"ext_mac_addr"      : ("Extended MAC Address Base",   "0x0C", 12),
		"prod_sub_ver"      : ("Product Sub Version",         "0x0D",  1)
              }

product_dict = { "Montara"   : "Wedge100BF-32X-O-AC-F-BF",
                 "Lower MAV" : "Wedge100BF-65X-O-AC-F-BF",
                 "Upper MAV" : "Wedge100BF-65X-O-AC-F-BF"
               }

thrift_server = 'localhost'
transport = None
pltfm_mgr = None

EEPROM_SYMLINK = "/var/run/platform/eeprom/syseeprom"
EEPROM_STATUS = "/var/run/platform/eeprom/status"

class board(eeprom_tlvinfo.TlvInfoDecoder):
    RETRIES = 35

    def __init__(self, name, path, cpld_root, ro):

        with open(os.path.dirname(__file__) + "/logging.conf", 'r') as f:
            config_dict = yaml.load(f)
            logging.config.dictConfig(config_dict)

        if not os.path.exists(os.path.dirname(EEPROM_SYMLINK)):
            try:
                os.makedirs(os.path.dirname(EEPROM_SYMLINK))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        open(EEPROM_SYMLINK, 'a').close()
        f = open(EEPROM_STATUS, 'w')
        f.write("initializing..")
        f.close()

        self.eeprom_path = EEPROM_SYMLINK
        super(board, self).__init__(self.eeprom_path, 0, EEPROM_STATUS, True)

        for attempt in range(self.RETRIES):
            if self.eeprom_init():
                break
            if attempt + 1 == self.RETRIES:
                raise RuntimeError("eeprom.py: Initialization failed")
            time.sleep(1)

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

    def eeprom_init(self):
        global pltfm_mgr

        try:
            self.thrift_setup()
            eeprom = pltfm_mgr.pltfm_mgr_sys_eeprom_get()
            self.thrift_teardown()
        except:
            return False

        f = open(EEPROM_STATUS, 'w')
        f.write("ok")
        f.close()

        eeprom_params = ""
        for attr, val in eeprom.__dict__.iteritems():
            if val is None:
                continue

            elem = eeprom_default_dict.get(attr)
            if elem is None:
                continue

            if isinstance(val, basestring):
                value = val.replace('\0', '')
            else:
                value = str(val)

            if attr == "sys_mfg_date":
                value = datetime.datetime.strptime(value, '%m-%d-%y').strftime('%m/%d/%Y 00:00:00')

            product = product_dict.get(value)
            if product is not None:
                value = product
            if len(eeprom_params) > 0:
                eeprom_params += ","
            eeprom_params += "{0:s}={1:s}".format(elem[1], value)

        orig_stdout = sys.stdout
        sys.stdout = StringIO()
        new_e = eeprom_tlvinfo.TlvInfoDecoder.set_eeprom(self, "", [eeprom_params])
        sys.stdout = orig_stdout
        eeprom_base.EepromDecoder.write_eeprom(self, new_e)

        return True


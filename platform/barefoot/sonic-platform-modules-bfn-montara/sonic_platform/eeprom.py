try:
    import os
    import sys
    import errno
    import datetime
    import logging
    import logging.config
    import yaml
    import re

    sys.path.append(os.path.dirname(__file__))

    if sys.version_info.major == 3:
        from io import StringIO
    else:
        from cStringIO import StringIO

    from sonic_platform_base.sonic_eeprom import eeprom_base
    from sonic_platform_base.sonic_eeprom import eeprom_tlvinfo

    from platform_thrift_client import thrift_try
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


_platform_eeprom_map = {
	"prod_name"         : ("Product Name",                "0x21", 12),
	"odm_pcba_part_num" : ("Part Number",                 "0x22", 13),
	"prod_ser_num"      : ("Serial Number",               "0x23", 12),
	"ext_mac_addr"      : ("Extended MAC Address Base",   "0x24", 12),
	"sys_mfg_date"      : ("System Manufacturing Date",   "0x25",  4),
	"prod_ver"          : ("Product Version",             "0x26",  1),
	"ext_mac_addr_size" : ("Extende MAC Address Size",    "0x2A",  2),
	"sys_mfger"         : ("Manufacturer",                "0x2B",  8)
}

_product_dict = { "Montara"   : "Wedge100BF-32X-O-AC-F-BF",
                 "Lower MAV" : "Wedge100BF-65X-O-AC-F-BF",
                 "Upper MAV" : "Wedge100BF-65X-O-AC-F-BF"
               }

_EEPROM_SYMLINK = "/var/run/platform/eeprom/syseeprom"
_EEPROM_STATUS = "/var/run/platform/eeprom/status"

try:
    _str_type = basestring
except NameError:
    _str_type = str

class Eeprom(eeprom_tlvinfo.TlvInfoDecoder):
    def __init__(self):
        with open(os.path.dirname(__file__) + "/logging.conf", 'r') as f:
            config_dict = yaml.load(f, yaml.SafeLoader)
            logging.config.dictConfig(config_dict)

        if not os.path.exists(os.path.dirname(_EEPROM_SYMLINK)):
            try:
                os.makedirs(os.path.dirname(_EEPROM_SYMLINK))
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise

        open(_EEPROM_SYMLINK, 'a').close()
        with open(_EEPROM_STATUS, 'w') as f:
            f.write("initializing..")

        self.eeprom_path = _EEPROM_SYMLINK
        super(Eeprom, self).__init__(self.eeprom_path, 0, _EEPROM_STATUS, True)

        def sys_eeprom_get(client):
            return client.pltfm_mgr.pltfm_mgr_sys_eeprom_get()
        try:
            platform_eeprom = thrift_try(sys_eeprom_get)
        except Exception:
            raise RuntimeError("eeprom.py: Initialization failed")

        self.__eeprom_init(platform_eeprom)

    def __eeprom_init(self, platform_eeprom):
        with open(_EEPROM_STATUS, 'w') as f:
            f.write("ok")

        eeprom_params = ""
        for attr, val in platform_eeprom.__dict__.items():
            if val is None:
                continue

            elem = _platform_eeprom_map.get(attr)
            if elem is None:
                continue

            if isinstance(val, _str_type):
                value = val.replace('\0', '')
            else:
                value = str(val)

            if attr == "sys_mfg_date":
                value = datetime.datetime.strptime(value, '%m-%d-%y').strftime('%m/%d/%Y 00:00:00')

            product = _product_dict.get(value)
            if product is not None:
                value = product
            if len(eeprom_params) > 0:
                eeprom_params += ","
            eeprom_params += "{0:s}={1:s}".format(elem[1], value)

        orig_stdout = sys.stdout
        sys.stdout = StringIO()
        try:
            eeprom_data = eeprom_tlvinfo.TlvInfoDecoder.set_eeprom(self, "", [eeprom_params])
        finally:
            decode_output = sys.stdout.getvalue()
            sys.stdout = orig_stdout

        eeprom_base.EepromDecoder.write_eeprom(self, eeprom_data)
        self.__eeprom_tlv_dict = self.__parse_output(decode_output)

    def __parse_output(self, decode_output):
        EEPROM_DECODE_HEADLINES = 6
        lines = decode_output.replace('\0', '').split('\n')
        lines = lines[EEPROM_DECODE_HEADLINES:]
        res = dict()

        for line in lines:
            try:
                # match whitespace-separated tag hex, length and value (value is mathced with its whitespaces)
                match = re.search('(0x[0-9a-fA-F]{2})([\s]+[\S]+[\s]+)([\S]+[\s]*[\S]*)', line)
                if match is not None:
                    code = match.group(1)
                    value = match.group(3).rstrip('\0')
                    res[code] = value
            except Exception:
                pass
        return res

    def __tlv_get(self, code):
        return self.__eeprom_tlv_dict.get("0x{:X}".format(code), 'N/A')

    def system_eeprom_info(self):
        return self.__eeprom_tlv_dict

    def serial_number_str(self):
        return self.__tlv_get(self._TLV_CODE_SERIAL_NUMBER)

    def serial_str(self):
        return self.serial_number_str()

    def base_mac_addr(self):
        return self.__tlv_get(self._TLV_CODE_MAC_BASE)

    def part_number_str(self):
        return self.__tlv_get(self._TLV_CODE_PART_NUMBER)

    def modelstr(self):
        return self.__tlv_get(self._TLV_CODE_PRODUCT_NAME)

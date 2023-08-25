import os
import sys
import json
import hashlib

import sonic_platform


if __name__ == "__main__":
    eeprom = sonic_platform.platform.Platform().get_chassis().get_eeprom()

    try:
        from sonic_platform.eeprom import Tlv

        mac = eeprom.get_mac()
        sn = eeprom.get_serial()
    except ImportError:
        try:
            from sonic_platform.eeprom import Eeprom

            mac = eeprom.base_mac_addr()
            sn = eeprom.serial_number_str()
        except ImportError:
            sys.exit(1)

    skey_path = "/host/skey/skey.json"

    try:
        with open(skey_path, "r+") as f:
            try:
                skey_data = json.load(f)
            except json.decoder.JSONDecodeError:
                sys.exit(3)

            if "ServiceKey" not in skey_data:
                sys.exit(4)

            skey_data["SerialNumber"] = sn
            skey_data["MacAddress"] = mac

            m = hashlib.sha256()
            m.update(skey_data["ServiceKey"].encode("UTF-8"))
            m.update(skey_data["SerialNumber"].encode("UTF-8"))
            m.update(skey_data["MacAddress"].encode("UTF-8"))
            m.update("edgecore".encode("UTF-8"))

            skey_data["SecurityCode"] = m.hexdigest()

            f.seek(0)
            f.truncate()
            json.dump(skey_data, f, indent=2)

    except Exception:
        sys.exit(2)


#
# Module contains an implementation of SONiC PSU Base API and
# provides the PSUs status which are available in the platform
#

try:
    import os.path
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)
        self.psu_status = "ipmitool raw 0x06 0x52 0x07 0x62 0x01 0x21"

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
        
        status = 0
        try:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x62 0x01 0x23").readline().strip()
            reg_value = int(content, 16)
            mask = (1 << (index - 1))
            if reg_value & mask == 0:
                status = 0
            else:
                status = 1
        except IOError:
            return False
        return status == 1


    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by 1-based index <index>

        :param index: An integer, 1-based index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        if index is None:
            return False

        status = 0
        try:
            content = os.popen("ipmitool raw 0x06 0x52 0x07 0x62 0x01 0x21").readline().strip()
            reg_value = int(content, 16)
            mask = (1 << (index - 1))
            if reg_value & mask != 0:
                status = 0
            else:
                status = 1
        except IOError:
            return False
        return status == 1


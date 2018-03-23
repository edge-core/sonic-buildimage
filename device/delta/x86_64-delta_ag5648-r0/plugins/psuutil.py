import os.path

try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)

        self.psu_path = "/sys/bus/i2c/devices/6-00{}/"
        self.psu_oper_status = "in1_input"
        self.psu_presence = "i2cget -y 6 0x{} 0x00"


    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device

        :return: An integer, the number of PSUs available on the device
        """
        return 2

    def get_psu_status(self, index):
        if index is None:
            return False
        Base_bus_number = 57
        status = 0
        try:
            with open(self.psu_path.format(index + Base_bus_number) + self.psu_oper_status, 'r') as power_status:
                if int(power_status.read()) == 0 :
                    return False
                else:
                    status = 1
        except IOError:
            return False
        return status == 1

    def get_psu_presence(self, index):
        if index is None:
            return False
        Base_bus_number = 49
        status = 0
        try:
            p = os.popen(self.psu_presence.format(index + Base_bus_number)+ "> /dev/null 2>&1")
            if p.readline() != None:
                status = 1
            p.close()
        except IOError:
            return False
        return status == 1



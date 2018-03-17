#
# psuutil.py
# Platform-specific PSU status interface for SONiC
#


import os.path

try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    SYS_GPIO_DIR = "/sys/class/gpio/"

    def __init__(self):
        PsuBase.__init__(self)


    # Get sysfs attribute
    def get_attr_value(self, attr_path):

        retval = 'ERR'
        if (not os.path.isfile(attr_path)):
            return retval

        try:
            with open(attr_path, 'r') as fd:
                retval = fd.read()
        except Exception as error:
            logging.error("Unable to open ", attr_path, " file !")

        retval = retval.rstrip('\r\n')
        return retval

    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
         """
        MAX_PSUS = 2
        return MAX_PSUS

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by index <index>
        :param index: An integer, index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is\
        faulty
        """
        status = 0
        gpio_path = [ 'gpio99/value', 'gpio96/value' ]
        attr_path = self.SYS_GPIO_DIR + gpio_path[index-1]

        attr_value = self.get_attr_value(attr_path)

        if (attr_value != 'ERR'):
            attr_value = int(attr_value, 10)
            # Check for PSU status
            if (attr_value == 1):
                    status = 1

        return status

    def get_psu_presence(self, index):
        """
        Retrieves the presence status of power supply unit (PSU) defined
                by index <index>
        :param index: An integer, index of the PSU of which to query status
        :return: Boolean, True if PSU is plugged, False if not
        """
        status = 0
        gpio_path = [ 'gpio100/value', 'gpio97/value' ]
        attr_path = self.SYS_GPIO_DIR + gpio_path[index-1]

        attr_value = self.get_attr_value(attr_path)

        if (attr_value != 'ERR'):
            attr_value = int(attr_value, 10)
            # Check for PSU status
            if (attr_value == 1):
                    status = 1

        return status


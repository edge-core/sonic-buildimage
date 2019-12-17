#
# psuutil.py
# Platform-specific PSU status interface for SONiC
#


import os.path
import logging
import commands
import sys


Z9332F_MAX_PSUS = 2
IPMI_PSU1_DATA = "docker exec -it pmon ipmitool raw 0x04 0x2d 0x2f |  awk '{print substr($0,9,1)}'"
IPMI_PSU1_DATA_DOCKER = "ipmitool raw 0x04 0x2d 0x2f |  awk '{print substr($0,9,1)}'"
IPMI_PSU2_DATA = "docker exec -it pmon ipmitool raw 0x04 0x2d 0x39 |  awk '{print substr($0,9,1)}'"
IPMI_PSU2_DATA_DOCKER = "ipmitool raw 0x04 0x2d 0x39 |  awk '{print substr($0,9,1)}'"
PSU_PRESENCE = "PSU{0}_Status"
# Use this for older firmware
# PSU_PRESENCE="PSU{0}_prsnt"
ipmi_sdr_list = ""


try:
    from sonic_psu.psu_base import PsuBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class PsuUtil(PsuBase):
    """Platform-specific PSUutil class"""

    def __init__(self):
        PsuBase.__init__(self)

    def isDockerEnv(self):
        num_docker = open('/proc/self/cgroup', 'r').read().count(":/docker")
        if num_docker > 0:
            return True
        else:
            return False

    # Fetch a BMC register
    def get_pmc_register(self, reg_name):

        status = 1
        global ipmi_sdr_list
        ipmi_dev_node = "/dev/pmi0"
        ipmi_cmd_1 = IPMI_PSU1_DATA
        ipmi_cmd_2 = IPMI_PSU1_DATA
        dockerenv = self.isDockerEnv()
        if dockerenv == True:
           if index == 1:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU1_DATA_DOCKER)
           elif index == 2:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU2_DATA_DOCKER)
        else:
           if index == 1:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU1_DATA)
           elif index == 2:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU2_DATA)

        if status:
            logging.error('Failed to execute ipmitool')
            sys.exit(0)

        output = ipmi_sdr_list

        return output

    def get_num_psus(self):
        """
        Retrieves the number of PSUs available on the device
        :return: An integer, the number of PSUs available on the device
         """
        Z9332F_MAX_PSUS = 2
        return Z9332F_MAX_PSUS

    def get_psu_status(self, index):
        """
        Retrieves the oprational status of power supply unit (PSU) defined
                by index <index>
        :param index: An integer, index of the PSU of which to query status
        :return: Boolean, True if PSU is operating properly, False if PSU is\
        faulty
        """
        # Until psu_status is implemented this is hardcoded temporarily

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
        ret_status = 1
        global ipmi_sdr_list
        ipmi_dev_node = "/dev/pmi0"
        dockerenv = self.isDockerEnv()
        if dockerenv == True:
           if index == 1:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU1_DATA_DOCKER)
           elif index == 2:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU2_DATA_DOCKER)
        else:
           if index == 1:
              status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU1_DATA)
           elif index == 2:
              ret_status, ipmi_sdr_list = commands.getstatusoutput(IPMI_PSU2_DATA)

        #if ret_status:
         #   print ipmi_sdr_list
         #   logging.error('Failed to execute ipmitool')
         #   sys.exit(0)

        psu_status = ipmi_sdr_list

        if psu_status == '1':
           status = 1

        return status


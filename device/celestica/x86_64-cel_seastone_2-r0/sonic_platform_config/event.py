#!/usr/bin/env python

#############################################################################
# Celestica Seastone2
#
# SfpEvent contains an implementation of SONiC Platform Base API
#
#############################################################################
try:
    import time
    import os
    from sonic_platform.common import Common
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


PLATFORM_PATH = "/sys/devices/platform/"
SWITCH_BRD_PLATFORM = "switchboard"
POLL_INTERVAL = 1


class SfpEvent:
    ''' Listen to insert/remove sfp events '''

    PORT_INFO_DIR = 'SFF'
    PATH_INT_SYSFS = "{0}/{port_name}/{type_prefix}_isr_flags"
    PATH_INTMASK_SYSFS = "{0}/{port_name}/{type_prefix}_isr_mask"
    PATH_PRS_SYSFS = "{0}/{port_name}/{prs_file_name}"
    PRESENT_EN = 0x01

    def __init__(self, sfp_list):
        self.num_sfp = len(sfp_list)
        self._api_common = Common()
        self._initialize_interrupts()

    def _initialize_interrupts(self):
        sfp_info_obj = {}
        port_info_path = os.path.join(
            PLATFORM_PATH, SWITCH_BRD_PLATFORM, self.PORT_INFO_DIR)

        for index in range(self.num_sfp):
            port_num = index + 1
            port_name = "QSFP{}".format(port_num)
            port_type = "qsfp"
            sysfs_prs_file = "{}_modprs".format(port_type)

            sfp_info_obj[index] = {}
            sfp_info_obj[index]['intmask_sysfs'] = self.PATH_INTMASK_SYSFS.format(
                port_info_path,
                port_name=port_name,
                type_prefix=port_type)

            sfp_info_obj[index]['int_sysfs'] = self.PATH_INT_SYSFS.format(
                port_info_path,
                port_name=port_name,
                type_prefix=port_type)

            sfp_info_obj[index]['prs_sysfs'] = self.PATH_PRS_SYSFS.format(
                port_info_path,
                port_name=port_name,
                prs_file_name=sysfs_prs_file)

            self._api_common.write_txt_file(
                sfp_info_obj[index]["intmask_sysfs"], hex(self.PRESENT_EN))

        self.sfp_info_obj = sfp_info_obj

    def _is_port_device_present(self, port_idx):
        prs_path = self.sfp_info_obj[port_idx]["prs_sysfs"]
        is_present = 1 - int(self._api_common.read_txt_file(prs_path))
        return is_present

    def _update_port_event_object(self, interrup_devices, port_dict):
        for port_idx in interrup_devices:
            device_id = str(port_idx + 1)
            port_dict[device_id] = str(self._is_port_device_present(port_idx))
        return port_dict

    def _clear_event_flag(self, path):
        self._api_common.write_txt_file(path, hex(0xff))
        time.sleep(0.1)
        self._api_common.write_txt_file(path, hex(0x0))

    def _check_all_port_interrupt_event(self):
        interrupt_devices = {}
        for i in range(self.num_sfp):
            int_sysfs = self.sfp_info_obj[i]["int_sysfs"]
            interrupt_flags = self._api_common.read_txt_file(int_sysfs)
            if interrupt_flags != '0x00':
                interrupt_devices[i] = 1
                self._clear_event_flag(int_sysfs)
        return interrupt_devices

    def get_event(self, timeout):
        sleep_time = min(
            timeout, POLL_INTERVAL) if timeout != 0 else POLL_INTERVAL
        start_milli_time = int(round(time.time() * 1000))
        int_sfp = {}

        while True:
            chk_sfp = self._check_all_port_interrupt_event()
            int_sfp = self._update_port_event_object(
                chk_sfp, int_sfp) if chk_sfp else int_sfp
            current_milli_time = int(round(time.time() * 1000))
            if (int_sfp) or \
                    (timeout != 0 and current_milli_time - start_milli_time > timeout):
                break

            time.sleep(sleep_time)

        change_dict = dict()
        change_dict['sfp'] = int_sfp

        return True, change_dict

#!/usr/bin/env python
#
# Name: chassis.py, version: 1.0
#
# Description: Module contains the definitions of SONiC platform APIs 
# which provide the chassis specific details
#
# Copyright (c) 2019, Juniper Networks, Inc.
# All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the GNU General 
# Public License as published by the Free Software Foundation, version 3 or 
# any later version. This code is not an official Juniper product. You can 
# obtain a copy of the License at <https://www.gnu.org/licenses/>
#
# OSS License:
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Third-Party Code: This code may depend on other components under separate 
# copyright notice and license terms.  Your use of the source code for those 
# components is subject to the terms and conditions of the respective license 
# as noted in the Third-Party source code file.
#

try:
    import os
    import commands
    import sys
    import time
    from sonic_platform_base.chassis_base import ChassisBase
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Chassis(ChassisBase):
    """
    JUNIPER QFX5210 Platform-specific Chassis class
    """

    # Find the last reboot reason out of following
    # CPLD_WATCHDOG_RESET    0x08
    # POWER_ON_RESET         0x20
    # CPU_WATCHDOG_RESET     0x40
    # SOFTWARE_RESET         0x80

    def __init__(self):
        ChassisBase.__init__(self)

    def get_qfx5210_parameter_value(self,parameter_name):
        try:
            with open("/var/run/eeprom", "r") as file:
                for item in file:
                    content = item.split('=')
                    if content[0] == parameter_name:
                        return content[1:]
                return "False"
        except IOError:
            print "Error: File not found"
            return "False"

    def get_product_name(self):
        product_name_list = self.get_qfx5210_parameter_value('Product Name')
        if product_name_list:
            product_name = ''.join(product_name_list)
            return product_name
        else:
            return False


    def get_part_number(self):
        part_number_list = self.get_qfx5210_parameter_value('Part Number')
        if part_number_list:
            part_number = ''.join(part_number_list)
            return part_number
        else:
            return False


    def get_serial_number(self):
        serial_number_list = self.get_qfx5210_parameter_value('Serial Number')
        if serial_number_list:
            serial_number = ''.join(serial_number_list)
            return serial_number
        else:
            return False


    def get_base_mac(self):
        mac_list = self.get_qfx5210_parameter_value('MAC')
        if mac_list:
            mac = ''.join(mac_list)
            return mac
        else:
            return False


    def get_mfg_date(self):
        mfgdate_list = self.get_qfx5210_parameter_value('Manufacture Date')
        if mfgdate_list:
            mfgdate = ''.join(mfgdate_list)
            return mfgdate
        else:
            return False

    def get_deviceversion_name(self):
        device_version_list = self.get_qfx5210_parameter_value('Device Version')
        if device_version_list:
            deviceversion_name = ''.join(device_version_list)
            return deviceversion_name
        else:
            return False

    def get_platform_name(self):
        platform_name_list = self.get_qfx5210_parameter_value('Platform Name')
        if platform_name_list:
            platform_name = ''.join(platform_name_list)
            return platform_name
        else:
            return False
    
    def get_MACnumber_name(self):
        MACnumber_name_list = self.get_qfx5210_parameter_value('Number of MAC Addresses')
        if MACnumber_name_list:
            MACnumber_name = ''.join(MACnumber_name_list)
            return MACnumber_name
        else:
            return False

    def get_vendor_name(self):
        vendor_name_list = self.get_qfx5210_parameter_value('Vendor Name')
        if vendor_name_list:
            vendor_name = ''.join(vendor_name_list)
            return vendor_name
        else:
            return False

    def get_mfg_name(self):
        mfg_name_list = self.get_qfx5210_parameter_value('Manufacture Name')
        if mfg_name_list:
            mfg_name = ''.join(mfg_name_list)
            return mfg_name
        else:
            return False

    def get_vendorext_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Vendor Extension')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextIANA_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('IANA')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextASMREV_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Assembly Part Number Rev')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextASMPartNum_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Assembly Part Number')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextASMID_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Assembly ID')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextASMMajNum_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Assembly Major Revision')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextASMMinNum_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('Assembly Minor Revision')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_vendorextCLEI_name(self):
        vendorext_list = self.get_qfx5210_parameter_value('CLEI code')
        if vendorext_list:
            vendorext = ''.join(vendorext_list)
            return vendorext
        else:
            return False

    def get_onieversion_name(self):
        onieversion_name_list = self.get_qfx5210_parameter_value('ONIE Version')
        if onieversion_name_list:
            onieversion_name = ''.join(onieversion_name_list)
            return onieversion_name
        else:
            return False

    def get_crc_name(self):
        crc_list = self.get_qfx5210_parameter_value('CRC')
        if crc_list:
            crc_name = ''.join(crc_list)
            return crc_name
        else:
            return False

    def get_fan_type(self, fantype_path):
        try:
            fan_type_file = open(fantype_path)
        except IOError as e:
            print "Error: unable to open file: %s" % str(e)
            return "-1"
        else:
            fan_type = fan_type_file.read()
            fan_type_file.close()
            return str(fan_type)


    def get_reboot_cause(self):
        """
        Retrieves the cause of the previous reboot
        """
        status, last_reboot_reason = commands.getstatusoutput("i2cget -y 0 0x65 0x24")
        if (status == 0):
            if last_reboot_reason == "0x80":
                return (ChassisBase.REBOOT_CAUSE_NON_HARDWARE, None)
            elif last_reboot_reason == "0x40" or last_reboot_reason == "0x08":
                return (ChassisBase.REBOOT_CAUSE_WATCHDOG, None)
            elif last_reboot_reason == "0x20":
                return (ChassisBase.REBOOT_CAUSE_POWER_LOSS, None)
            elif last_reboot_reason == "0x10":
                return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Swizzle Reset")
            else:
                return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Unknown reason")
        else:
            time.sleep(3)
            status, last_reboot_reason = commands.getstatusoutput("i2cget -y 0 0x65 0x24")
            if last_reboot_reason == "0x80":
                return (ChassisBase.REBOOT_CAUSE_NON_HARDWARE, None)
            elif last_reboot_reason == "0x40" or last_reboot_reason == "0x08":
                return (ChassisBase.REBOOT_CAUSE_WATCHDOG, None)
            elif last_reboot_reason == "0x20":
                return (ChassisBase.REBOOT_CAUSE_POWER_LOSS, None)
            elif last_reboot_reason == "0x10":
                return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Swizzle Reset")
            else:
                return (ChassisBase.REBOOT_CAUSE_HARDWARE_OTHER, "Unknown reason")

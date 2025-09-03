# SPDX-License-Identifier: MIT
#
# Copyright (c) 2024 Xsightlabs Ltd.

import tabulate as tb
import chassis

tb.PRESERVE_WHITESPACE = True

chassistest = chassis.Chassis()

print("\n Loop over chassis psus")
num_psus = chassistest.get_num_psus()
psu_list = chassistest.get_all_psus()
psu_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'voltage[V]', 'current[A]',
              'power[W]', 'temp[C]', 'led']
psu_tb_list = []
for psu in range(num_psus):
        tmp_list = []
        tmp_list.append(psu_list[psu].get_name())
        tmp_list.append(psu_list[psu].get_presence())
        tmp_list.append(psu_list[psu].get_status())
        tmp_list.append(psu_list[psu].get_model().rstrip())
        tmp_list.append(psu_list[psu].get_serial().rstrip())
        tmp_list.append(psu_list[psu].get_voltage())
        tmp_list.append(psu_list[psu].get_current())
        tmp_list.append(psu_list[psu].get_power())
        tmp_list.append(psu_list[psu].get_temperature())
        tmp_list.append(psu_list[psu].get_status_led())
        psu_tb_list.append(tmp_list)
print(tb.tabulate(psu_tb_list, headers=psu_tb_hdr, tablefmt="grid"))

print("\n Loop over fans in chassis psus")
psu_fan_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'direction', 'speed',
                  'target_speed', 'speed_tolerance', 'led']
psu_fan_tb_list = []
for psu in range(num_psus):
        num_fans_in_psu = psu_list[psu].get_num_fans()
        psu_fan_list = psu_list[psu].get_all_fans()
        for fan in range(num_fans_in_psu):
                tmp_list = []
                tmp_list.append(psu_fan_list[fan].get_name())
                tmp_list.append(psu_fan_list[fan].get_presence())
                tmp_list.append(psu_fan_list[fan].get_status())
                tmp_list.append(psu_fan_list[fan].get_model())
                tmp_list.append(psu_fan_list[fan].get_serial())
                tmp_list.append(psu_fan_list[fan].get_direction())
                tmp_list.append(psu_fan_list[fan].get_speed())
                tmp_list.append(psu_fan_list[fan].get_target_speed())
                tmp_list.append(psu_fan_list[fan].get_speed_tolerance())
                tmp_list.append(psu_fan_list[fan].get_status_led())
                psu_fan_tb_list.append(tmp_list)
print(tb.tabulate(psu_fan_tb_list, headers=psu_fan_tb_hdr, tablefmt="grid"))

print("\n Loop over chassis fan drawers")
num_fan_drawers = chassistest.get_num_fan_drawers()
fan_drawer_list = chassistest.get_all_fan_drawers()
fan_drawer_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'max_power']
fan_drawer_tb_list = []
for fan_drawer in range(num_fan_drawers):
        tmp_list = []
        tmp_list.append(fan_drawer_list[fan_drawer].get_name())
        tmp_list.append(fan_drawer_list[fan_drawer].get_presence())
        tmp_list.append(fan_drawer_list[fan_drawer].get_status())
        tmp_list.append(fan_drawer_list[fan_drawer].get_model())
        tmp_list.append(fan_drawer_list[fan_drawer].get_serial())
        tmp_list.append(fan_drawer_list[fan_drawer].get_maximum_consumed_power())
        fan_drawer_tb_list.append(tmp_list)
print(tb.tabulate(fan_drawer_tb_list, headers=fan_drawer_tb_hdr, tablefmt="grid"))

print("\n Loop over fans in chassis fan drawers")
fan_drawer_fan_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'direction',
                          'speed', 'target_speed', 'speed_tolerance', 'led']
fan_drawer_fan_tb_list = []
for fan_drawer in range(num_fan_drawers):
        num_fans_in_fan_drawer = fan_drawer_list[fan_drawer].get_num_fans()
        fan_drawer_fan_list = fan_drawer_list[fan_drawer].get_all_fans()
        for fan in range(num_fans_in_fan_drawer):
                tmp_list = []
                tmp_list.append(fan_drawer_fan_list[fan].get_name())
                tmp_list.append(fan_drawer_fan_list[fan].get_presence())
                tmp_list.append(fan_drawer_fan_list[fan].get_status())
                tmp_list.append(fan_drawer_fan_list[fan].get_model())
                tmp_list.append(fan_drawer_fan_list[fan].get_serial())
                tmp_list.append(fan_drawer_fan_list[fan].get_direction())
                tmp_list.append(fan_drawer_fan_list[fan].get_speed())
                tmp_list.append(fan_drawer_fan_list[fan].get_target_speed())
                tmp_list.append(fan_drawer_fan_list[fan].get_speed_tolerance())
                tmp_list.append(fan_drawer_fan_list[fan].get_status_led())
                fan_drawer_fan_tb_list.append(tmp_list)
print(tb.tabulate(fan_drawer_fan_tb_list, headers=fan_drawer_fan_tb_hdr, tablefmt="grid"))

print("\n Loop over chassis fans")
num_fans = chassistest.get_num_fans()
fan_list = chassistest.get_all_fans()
fan_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'direction', 'speed',
              'target_speed', 'speed_tolerance', 'led']
fan_tb_list = []
for fan in range(num_fans):
        tmp_list = []
        tmp_list.append(fan_list[fan].get_name())
        tmp_list.append(fan_list[fan].get_presence())
        tmp_list.append(fan_list[fan].get_status())
        tmp_list.append(fan_list[fan].get_model())
        tmp_list.append(fan_list[fan].get_serial())
        tmp_list.append(fan_list[fan].get_direction())
        tmp_list.append(fan_list[fan].get_speed())
        tmp_list.append(fan_list[fan].get_target_speed())
        tmp_list.append(fan_list[fan].get_speed_tolerance())
        tmp_list.append(fan_list[fan].get_status_led())
        fan_tb_list.append(tmp_list)
print(tb.tabulate(fan_tb_list, headers=fan_tb_hdr, tablefmt="grid"))

print("\n Loop over chassis thermals")
num_thermals = chassistest.get_num_thermals()
thermal_list = chassistest.get_all_thermals()
thermal_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'temp[C]', 'high_threshold']
thermal_tb_list = []
for thermal in range(num_thermals):
        tmp_list = []
        tmp_list.append(thermal_list[thermal].get_name())
        tmp_list.append(thermal_list[thermal].get_presence())
        tmp_list.append(thermal_list[thermal].get_status())
        tmp_list.append(thermal_list[thermal].get_model())
        tmp_list.append(thermal_list[thermal].get_serial())
        tmp_list.append(thermal_list[thermal].get_temperature())
        tmp_list.append(thermal_list[thermal].get_high_threshold())
        thermal_tb_list.append(tmp_list)
print(tb.tabulate(thermal_tb_list, headers=thermal_tb_hdr, tablefmt="grid"))

print("\n Loop over chassis components")
num_components = chassistest.get_num_components()
component_list = chassistest.get_all_components()
component_tb_hdr = ['name', 'presence', 'status', 'model', 'serial', 'version', 'description']
component_tb_list = []
for component in range(num_components):
        tmp_list = []
        tmp_list.append(component_list[component].get_name())
        tmp_list.append(component_list[component].get_presence())
        tmp_list.append(component_list[component].get_status())
        tmp_list.append(component_list[component].get_model())
        tmp_list.append(component_list[component].get_serial())
        tmp_list.append(component_list[component].get_firmware_version())
        tmp_list.append(component_list[component].get_description())
        component_tb_list.append(tmp_list)
print(tb.tabulate(component_tb_list, headers=component_tb_hdr, tablefmt="grid"))

print("\n Loop over chassis sfps")
num_sfps = chassistest.get_num_sfps()
sfp_list = chassistest.get_all_sfps()
sfp_tb_hdr = ['name', 'presence', 'status', 'change_event', 'reset_status', 'lpmode']
sfp_tb_list = []
for sfp in range(num_sfps):
        tmp_list = []
        tmp_list.append(sfp_list[sfp].get_name())
        tmp_list.append(sfp_list[sfp].get_presence())
        tmp_list.append(sfp_list[sfp].get_status())
        tmp_list.append(sfp_list[sfp].get_transceiver_change_event())
        tmp_list.append(sfp_list[sfp].get_reset_status())
        tmp_list.append(sfp_list[sfp].get_lpmode())
        sfp_tb_list.append(tmp_list)
print(tb.tabulate(sfp_tb_list, headers=sfp_tb_hdr, tablefmt="grid"))

#!/usr/bin/env python

import  os
import  os . path

try:
    from sonic_platform.helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NULL_VAL = "N/A"

MISC_SENSORS_INFO = [
    {'name': 'BB_XP12R0V',    # 0
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in1_input'},
    {'name': 'BB_XP5R0V',    # 1
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in2_input'},
    {'name': 'COME_XP3R3V',    # 2
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in3_input'},
    {'name': 'COME_XP1R82V',    # 3
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in4_input'},
    {'name': 'COME_XP1R05V',  # 4
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in5_input'},
    {'name': 'COME_XP1R7V', # 5
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in6_input'},
    {'name': 'COME_XP1R2V', # 6
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in7_input'},
    {'name': 'COME_XP1R3V', # 7
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in8_input'},
    {'name': 'COME_XP1R5V', # 8
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in9_input'},
    {'name': 'COME_XP2R5V', # 9
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in10_input'},
    {'name': 'COME_XP12R0V', # 10
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in11_input'},
    {'name': 'SSD_XP3R3V', # 11
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0035/hwmon/hwmon*/in12_input'},
    {'name': 'SW_XP5R0V_C', # 12
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in1_input'},
    {'name': 'SW_XP3R3V_C',    # 13
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in2_input'},
    {'name': 'SW_XP3R3V_L',  # 14
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in3_input'},
    {'name': 'SW_XP3R3V_R',  # 15
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in4_input'},
    {'name': 'SW_XP3R3V_FPGA',  # 16
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in5_input'},
    {'name': 'SW_XP1R8V_FPGA',  # 17
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in6_input'},
    {'name': 'SW_XP1R8V_VDDH',  # 18
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in7_input'},
    {'name': 'SW_XP1R2V_FPGA',  # 19
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in8_input'},
    {'name': 'SW_XP1R0V_FPGA', # 20
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in9_input'},
    {'name': 'SW_XP1R1V_AVDDH', # 21
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in10_input'},
    {'name': 'SW_XP0R94V_AVDD1', # 22
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in11_input'},
    {'name': 'SW_XP0R94V_AVDD2',    # 23
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in12_input'},
    {'name': 'SW_XP0R9V_VDD',  # 24
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in13_input'},
    {'name': 'SW_XP0R9V_AVDD',  # 25
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in14_input'},
    {'name': 'SW_0R8V_VDD',  # 26
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in15_input'},
    {'name': 'SW_XP12R0V',  # 27
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-0034/hwmon/hwmon*/in16_input'},
    {'name': 'QSFP_DD_VOut1',  # 28
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-007b/hwmon/hwmon*/in2_input'},
    {'name': 'QSFP_DD_COut1',  # 29
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-007b/hwmon/hwmon*/curr2_input'},
    {'name': 'QSFP_DD_POut1', # 30
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-007b/hwmon/hwmon*/power2_input'},
    {'name': 'QSFP_DD_VOut2', # 31
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0076/hwmon/hwmon*/in2_input'},
    {'name': 'QSFP_DD_COut2', # 32
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0076/hwmon/hwmon*/curr2_input'},
    {'name': 'QSFP_DD_POut2',    # 33
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0076/hwmon/hwmon*/power2_input'},
    {'name': 'I89_AVDD_VOut1',  # 34
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/in2_input'},
    {'name': 'I89_AVDD_COut1',  # 35
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/curr2_input'},
    {'name': 'I89_AVDD_POut1',  # 36
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/power2_input'},
    {'name': 'I89_AVDDH_VOut2',  # 37
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/in3_input'},
    {'name': 'I89_AVDDH_COut2',  # 38
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/curr3_input'},
    {'name': 'I89_AVDDH_POut2',  # 39
     'sensor_path': 'i2cget -y -f 5 0x70 0x96 w'},
    {'name': 'I89_CORE_VOut', # 40
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-006c/hwmon/hwmon*/in2_input'},
    {'name': 'I89_CORE_COut', # 41
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-006c/hwmon/hwmon*/curr1_input'},
    {'name': 'I89_CORE_POut', # 42
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-006c/hwmon/hwmon*/power1_input'},
    {'name': 'I89_CORE_Temp',    # 43
     'sensor_path': '/sys/bus/i2c/devices/i2c-4/4-006c/hwmon/hwmon*/temp1_input'},
    {'name': 'I89_AVDD_Temp',  # 44
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0070/hwmon/hwmon*/temp1_input'},
    {'name': 'QSFP_DD_Temp1',  # 45
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-007b/hwmon/hwmon*/temp1_input'},
    {'name': 'QSFP_DD_Temp2',  # 46
     'sensor_path': '/sys/bus/i2c/devices/i2c-5/5-0076/hwmon/hwmon*/temp1_input'},
    {'name': 'PSU1_Fan',    # 47
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/fan1_input'},
    {'name': 'PSU2_Fan',    # 48
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/fan1_input'},
    {'name': 'Fan1_Front',  # 49
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan1_front_speed_rpm'},
    {'name': 'Fan2_Front', # 50
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan2_front_speed_rpm'},
    {'name': 'Fan3_Front', # 51
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan3_front_speed_rpm'},
    {'name': 'Fan4_Front', # 52
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan4_front_speed_rpm'},
    {'name': 'Fan5_Front', # 53
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan5_front_speed_rpm'},
    {'name': 'Fan6_Front',  # 54
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan6_front_speed_rpm'},
    {'name': 'Fan7_Front',  # 55
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan7_front_speed_rpm'},
    {'name': 'Fan1_Rear',  # 56
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan1_rear_speed_rpm'},
    {'name': 'Fan2_Rear',    # 57
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan2_rear_speed_rpm'},
    {'name': 'Fan3_Rear',    # 58
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan3_rear_speed_rpm'},
    {'name': 'Fan4_Rear',  # 59
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan4_rear_speed_rpm'},
    {'name': 'Fan5_Rear',  # 60
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan5_rear_speed_rpm'},
    {'name': 'Fan6_Rear',    # 61
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan6_rear_speed_rpm'},
    {'name': 'Fan7_Rear',    # 62
     'sensor_path': '/sys/bus/i2c/devices/i2c-9/9-000d/fan7_rear_speed_rpm'},
    {'name': 'PSU1_VIn', # 63
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/in1_input'},
    {'name': 'PSU1_CIn', # 64
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/curr1_input'},
    {'name': 'PSU1_PIn', # 65
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/power1_input'},
    {'name': 'PSU1_VOut',  # 66
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/in2_input'},
    {'name': 'PSU1_COut',  # 67
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/curr2_input'},
    {'name': 'PSU1_POut',  # 68
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0058/hwmon/hwmon*/power2_input'},     
    {'name': 'PSU2_VIn', # 69
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/in1_input'},
    {'name': 'PSU2_CIn', # 70
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/curr1_input'},
    {'name': 'PSU2_PIn', # 71
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/power1_input'},
    {'name': 'PSU2_VOut',  # 72
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/in2_input'},
    {'name': 'PSU2_COut',  # 73
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/curr2_input'},
    {'name': 'PSU2_POut',  # 74
     'sensor_path': '/sys/bus/i2c/devices/i2c-7/7-0059/hwmon/hwmon*/power2_input'},
]

misc_sensors_threshold = {
    "BB_XP12R0V": {"low_critical_threshold": 10200, "min": 10800, "max": 13200, "high_critical_threshold": 13800},
    "BB_XP5R0V": {"low_critical_threshold": 4230, "min": 4500, "max": 5490, "high_critical_threshold": 5730},
    "COME_XP3R3V": {"low_critical_threshold": 2800, "min": 2960, "max": 3620, "high_critical_threshold": 3800},
    "COME_XP1R82V": {"low_critical_threshold": 1550, "min": 1640, "max": 2000, "high_critical_threshold": 2090},
    "COME_XP1R05V": {"low_critical_threshold": 890, "min": 950,
                   "max": 1160, "high_critical_threshold": 1210},
    "COME_XP1R7V": {"low_critical_threshold": 1450, "min": 1530,
                    "max": 1870, "high_critical_threshold": 1960},
    "COME_XP1R2V": {"low_critical_threshold": 1020, "min": 1080,
                    "max": 1320, "high_critical_threshold": 1380},
    "COME_XP1R3V": {"low_critical_threshold": 1110, "min": 1170,
                    "max": 1430, "high_critical_threshold": 1500},
    "COME_XP1R5V": {"low_critical_threshold": 1280, "min": 1350,
                    "max": 1650, "high_critical_threshold": 1720},
    "COME_XP2R5V": {"low_critical_threshold": 2120, "min": 2240,
                     "max": 2740, "high_critical_threshold": 2860},
    "COME_XP12R0V": {"low_critical_threshold": 10200, "min": 10800,
                     "max": 13200, "high_critical_threshold": 13800},
    "SSD_XP3R3V": {"low_critical_threshold": 2800, "min": 2960,
                     "max": 3620, "high_critical_threshold": 3800},
    "SW_XP5R0V_C": {"low_critical_threshold": 4260, "min": 4500,
                     "max": 5490, "high_critical_threshold": 5760},
    "SW_XP3R3V_C": {"low_critical_threshold": 2800, "min": 2980,
                     "max": 3620, "high_critical_threshold": 3800},
    "SW_XP3R3V_L": {"low_critical_threshold": 2800, "min": 2980,
                   "max": 3620, "high_critical_threshold": 3800},
    "SW_XP3R3V_R": {"low_critical_threshold": 2800, "min": 2980,
                   "max": 3620, "high_critical_threshold": 3800},
    "SW_XP3R3V_FPGA": {"low_critical_threshold": 2800, "min": 2980,
                   "max": 3620, "high_critical_threshold": 3800},
    "SW_XP1R8V_FPGA": {"low_critical_threshold": 1530, "min": 1620,
                   "max": 1980, "high_critical_threshold": 2070},
    "SW_XP1R8V_VDDH": {"low_critical_threshold": 1530, "min": 1620,
                   "max": 1980, "high_critical_threshold": 2070},
    "SW_XP1R2V_FPGA": {"low_critical_threshold": 1020, "min": 1080,
                   "max": 1320, "high_critical_threshold": 1380},           
    "SW_XP1R0V_FPGA": {"low_critical_threshold": 850, "min": 900,
                   "max": 1100, "high_critical_threshold": 1150},
    "SW_XP1R1V_AVDDH": {"low_critical_threshold": 940, "min": 990,
                   "max": 1210, "high_critical_threshold": 1270},
    "SW_XP0R94V_AVDD1": {"low_critical_threshold": 800, "min": 850,
                   "max": 1030, "high_critical_threshold": 1080},
    "SW_XP0R94V_AVDD2": {"low_critical_threshold": 800, "min": 850,
                   "max": 1030, "high_critical_threshold": 1080},
    "SW_XP0R9V_VDD": {"low_critical_threshold": 770, "min": 810,
                   "max": 990, "high_critical_threshold": 1040},
    "SW_XP0R9V_AVDD": {"low_critical_threshold": 770, "min": 810,
                   "max": 990, "high_critical_threshold": 1040},
    "SW_0R8V_VDD": {"low_critical_threshold": 680, "min": 720,
                   "max": 880, "high_critical_threshold": 920},
    "SW_XP12R0V": {"low_critical_threshold": 10200, "min": 10800,
                   "max": 13200, "high_critical_threshold": 13800},                   
    "QSFP_DD_VOut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_COut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_POut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_VOut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_COut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_POut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDD_VOut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDD_COut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDD_POut1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDDH_VOut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDDH_COut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDDH_POut2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_CORE_VOut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_CORE_COut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_CORE_POut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_CORE_Temp": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "I89_AVDD_Temp": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_Temp1": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "QSFP_DD_Temp2": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": NULL_VAL},
    "PSU1_Fan": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": 33400, "high_critical_threshold": NULL_VAL},
    "PSU2_Fan": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL, "max": 33400, "high_critical_threshold": NULL_VAL},
    "Fan1_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                   "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan2_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                    "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan3_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                    "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan4_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                    "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan5_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                    "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan6_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                     "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan7_Front": {"low_critical_threshold": 2200, "min": NULL_VAL,
                     "max": 37800, "high_critical_threshold": NULL_VAL},
    "Fan1_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                     "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan2_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                    "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan3_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                    "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan4_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                     "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan5_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                     "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan6_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                     "max": 40000, "high_critical_threshold": NULL_VAL},
    "Fan7_Rear": {"low_critical_threshold": 2400, "min": NULL_VAL,
                     "max": 40000, "high_critical_threshold": NULL_VAL},
    "PSU1_VIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": 239800, "high_critical_threshold": 264000},
    "PSU1_CIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": 14080},
    "PSU1_PIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": 1500000000},
    "PSU1_VOut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": 13500, "high_critical_threshold": 15600},
    "PSU1_COut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": 125000, "high_critical_threshold": NULL_VAL},
    "PSU1_POut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 1500000000},
    "PSU2_VIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                   "max": 239800, "high_critical_threshold": 264000},
    "PSU2_CIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": 14080},
    "PSU2_PIn": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": NULL_VAL, "high_critical_threshold": 1500000000},
    "PSU2_VOut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": 13500, "high_critical_threshold": 15600},
    "PSU2_COut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                    "max": 125000, "high_critical_threshold": NULL_VAL},
    "PSU2_POut": {"low_critical_threshold": NULL_VAL, "min": NULL_VAL,
                     "max": NULL_VAL, "high_critical_threshold": 1500000000},
}

class MiscSensors():

    def __init__(self, Voltage_index):

        self.index = Voltage_index
        self._api_helper  =  APIHelper ()
        self._misc_sensors_info = MISC_SENSORS_INFO[self.index]
        self.name = self.get_name()

    def get_miscsensors_value(self):
        path = self._misc_sensors_info.get("sensor_path", "N/A")
        if "i2cget" in path:
            status, voltage = self._api_helper.run_command(path)
            voltage = int(voltage, 16)
        else:
            path = os.popen("ls %s" % path).read().strip()
            voltage = self._api_helper.read_txt_file(path)
            if voltage:
                voltage = int(voltage)
            else:
                voltage = 0

        return voltage

    def get_high_threshold(self):
        """
        Retrieves the high threshold voltage of Voltage
        Returns:
            A float number, the high threshold voltage of Voltage in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        high_threshold = misc_sensors_threshold.get(self.name).get("max")

        return high_threshold

    def get_low_threshold(self):
        """
        Retrieves the low threshold voltage of Voltage
        Returns:
            A float number, the low threshold voltage of Voltage in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        low_threshold = misc_sensors_threshold.get(self.name).get("min")
        return low_threshold

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold voltage of Voltage
        Returns:
            A float number, the high critical threshold voltage of Voltage in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        high_critical_threshold = misc_sensors_threshold.get(self.name).get("high_critical_threshold")
        return high_critical_threshold

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold voltage of Voltage
        Returns:
            A float number, the low critical threshold voltage of Voltage in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        low_critical_threshold = misc_sensors_threshold.get(self.name).get("low_critical_threshold")
        return low_critical_threshold

    def get_name(self):
        """
        Retrieves the name of the Voltage device
            Returns:
            string: The name of the Voltage device
        """
        return self._misc_sensors_info.get("name")

    def get_presence(self):
        """
        Retrieves the presence of the PSU
        Returns:
            bool: True if PSU is present, False if not
        """
        return os.path.isfile(self._misc_sensors_info.get("sensor_path", NULL_VAL))

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        if not self.get_presence():
            return  False
        return True

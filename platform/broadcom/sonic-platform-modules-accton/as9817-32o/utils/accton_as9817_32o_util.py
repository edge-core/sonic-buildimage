#!/usr/bin/env python3
#
# Copyright (C) 2016 Accton Networks, Inc.
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
usage: accton_as9817_32o_util.py [-h] [-d] [-f] {install,clean,threshold} ...

AS9817-32O Platform Utility

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           run with debug mode
  -f, --force           ignore error during installation or clean

Utility Command:
  {install,clean,threshold}
    install             : install drivers and generate related sysfs nodes
    clean               : uninstall drivers and remove related sysfs nodes
    threshold           : modify thermal threshold
"""
import subprocess
import sys
import logging
import re
import time
import os
import glob
import argparse
from sonic_py_common.general import getstatusoutput_noshell


PROJECT_NAME = 'as9817_32o'
version = '0.1.0'
verbose = False
DEBUG = False
FAN_PWM = 67
args = []
FORCE = 0
CPU = 0
FRONT = 1
S_10G = 2
S_25G = 3
TI_MUX_I2C_BUS = '42'
TI_MUX_I2C_ADDR = '0x1b'
#logging.basicConfig(filename= PROJECT_NAME+'.log', filemode='w',level=logging.DEBUG)
#logging.basicConfig(level=logging.INFO)


if DEBUG == True:
    print(sys.argv[0])
    print('ARGV      :', sys.argv[1:])


def main():
    global DEBUG
    global args
    global FORCE
    global THRESHOLD_RANGE_LOW, THRESHOLD_RANGE_HIGH

    util_parser = argparse.ArgumentParser(description="AS9817-32O Platform Utility")
    util_parser.add_argument("-d", "--debug", dest='debug', action='store_true', default=False,
                             help="run with debug mode")
    util_parser.add_argument("-f", "--force", dest='force', action='store_true', default=False,
                             help="ignore error during installation or clean")
    subcommand = util_parser.add_subparsers(dest='cmd', title='Utility Command', required=True)
    subcommand.add_parser('install', help=': install drivers and generate related sysfs nodes')
    subcommand.add_parser('clean', help=': uninstall drivers and remove related sysfs nodes')
    sfp = subcommand.add_parser('sfp', help=': enable 10G to CPU or 10G/25G to front port')
    sfp.add_argument("-c", dest='cpu', action='store_true', default=False,
                     help="enable 10G to CPU")
    sfp.add_argument("-f10", dest='front10', action='store_true', default=False,
                     help="enable 10G to front port")
    sfp.add_argument("-f25", dest='front25', action='store_true', default=False,
                     help="enable 25G to front port")
    threshold_parser = subcommand.add_parser('threshold', help=': modify thermal threshold')
    threshold_parser.add_argument("-l", dest='list', action='store_true', default=False,
                                  help="list avaliable thermal")
    threshold_parser.add_argument("-t", dest='thermal', type=str, metavar='THERMAL_NAME',
                                  help="thermal name, ex: -t 'Temp sensor 1'")
    threshold_parser.add_argument("-ht", dest='high_threshold', type=restricted_float,
                                  metavar='THRESHOLD_VALUE',
                                  help="high threshold: %.1f ~ %.1f" % (THRESHOLD_RANGE_LOW, THRESHOLD_RANGE_HIGH))
    threshold_parser.add_argument("-hct", dest='high_crit_threshold', type=restricted_float,
                                  metavar='THRESHOLD_VALUE',
                                  help="high critical threshold : %.1f ~ %.1f" % (THRESHOLD_RANGE_LOW, THRESHOLD_RANGE_HIGH))
    args = util_parser.parse_args()

    if DEBUG == True:
        print(args)
        print(len(sys.argv))

    DEBUG = args.debug
    #FORCE = 1 if args.force else 0
    FORCE = 1

    if args.cmd == 'install':
        do_install()
    elif args.cmd == 'clean':
        do_uninstall()
    elif args.cmd == 'threshold':
        do_threshold()
    elif args.cmd == 'sfp':
        do_sfp()

    return 0

def show_help():
    print(__doc__ % {'scriptName' : sys.argv[0].split("/")[-1]})
    sys.exit(0)

def my_log(txt):
    if DEBUG == True:
        print("[DEBUG]"+txt)
    return

def log_os_system(cmd, show):
    logging.info('Run :'+cmd)
    status, output = subprocess.getstatusoutput(cmd)
    #status, output = getstatusoutput_noshell(cmd)
    my_log (cmd +"with result:" + str(status))
    my_log ("      output:"+output)
    if status:
        logging.info('Failed :'+cmd)
        if show:
            print('Failed :'+cmd)
    return  status, output

def driver_check():
    ret, lsmod = log_os_system("ls /sys/module/*accton*", 0)
    logging.info('mods:'+lsmod)
    if ret :
        return False
    else :
        return True

ipmi_ko = [
    'modprobe ipmi_msghandler',
    'modprobe ipmi_ssif',
    'modprobe ipmi_si',
    'modprobe ipmi_devintf']

ATTEMPTS = 5
INTERVAL = 3

def init_ipmi_dev_intf():
    attempts = ATTEMPTS
    interval = INTERVAL

    while attempts:
        for i in range(0, len(ipmi_ko)):
            subprocess.getstatusoutput(ipmi_ko[i])

        if os.path.exists('/dev/ipmi0') or os.path.exists('/dev/ipmidev/0'):
            return (0, (ATTEMPTS - attempts) * interval)

        for i in reversed(range(0, len(ipmi_ko))):
            rm = ipmi_ko[i].replace("modprobe", "modprobe -rq")
            subprocess.getstatusoutput(rm)

        attempts -= 1
        time.sleep(interval)

    return (1, ATTEMPTS * interval)

def init_ipmi_oem_cmd():
    attempts = ATTEMPTS
    interval = INTERVAL

    while attempts:
        status, output = subprocess.getstatusoutput('ipmitool raw 0x34 0x95')
        if status:
            attempts -= 1
            time.sleep(interval)
            continue

        return (0, (ATTEMPTS - attempts) * interval)

    return (1, ATTEMPTS * interval)

def init_ipmi():
    attempts = ATTEMPTS
    interval = 60

    while attempts:
        attempts -= 1

        (status, elapsed_dev) = init_ipmi_dev_intf()
        if status:
            time.sleep(max(0, interval - elapsed_dev))
            continue

        (status, elapsed_oem) = init_ipmi_oem_cmd()
        if status:
            time.sleep(max(0, interval - elapsed_dev - elapsed_oem))
            continue

        print('IPMI dev interface is ready.')
        return 0

    print('Failed to initialize IPMI dev interface')
    return 1


kos = [
    'modprobe i2c_dev',
    'modprobe i2c_i801',
    'modprobe i2c_ismt',
    'modprobe optoe',
    'modprobe at24',
    'modprobe i2c-ocores',
    'modprobe accton_as9817_32_fpga',
    'modprobe accton_as9817_32_fan',
    'modprobe accton_as9817_32_psu',
    'modprobe accton_as9817_32_thermal',
    'modprobe accton_as9817_32_sys',
    'modprobe accton_as9817_32_leds',
    'modprobe accton_as9817_32_mux'
]

#EERPOM
eeprom_mknod =[
    'echo 24c02 0x56 > /sys/bus/i2c/devices/i2c-36/new_device',
]

def eeprom_check():
    cmd = ["i2cget", "-f", "-y", "36", "0x56"]
    status, output = getstatusoutput_noshell(cmd)
    return status

def driver_install():
    global FORCE

    # Load 10G ethernet driver
    status, output = log_os_system("modprobe ice", 1)
    if status:
        if FORCE == 0:
            return status

    status = init_ipmi()
    if status:
        if FORCE == 0:
            return status

    status, output = log_os_system("depmod -ae", 1)
    for i in range(0,len(kos)):
        status, output = log_os_system(kos[i], 1)
        if status:
            if FORCE == 0:
                return status
    print("Done driver_install")

    return 0

def driver_uninstall():
    global FORCE

    for i in range(0,len(kos)):
        rm = kos[-(i+1)].replace("modprobe", "modprobe -rq")
        rm = rm.replace("insmod", "rmmod")
        lst = rm.split(" ")
        if len(lst) > 3:
            del(lst[3])
        rm = " ".join(lst)
        status, output = log_os_system(rm, 1)
        if status:
            if FORCE == 0:
                return status
    return 0

i2c_prefix = '/sys/bus/i2c/devices/'

sfp_map =  [
     2, 3, 4, 5, 6, 7, 8, 9,10,11,12,13,14,15,16,17,
    18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,
    34,35
]

osfp_start = 0
osfp_end   = 31

mknod =[
    'echo as9817_32_mux 0x78 > /sys/bus/i2c/devices/i2c-0/new_device'
]

mkfile = [
    '/tmp/device_threshold.json',
    '/tmp/device_threshold.json.lock'
]

def set_i2c_register(bus, device, register, value):
    cmd = ['/usr/sbin/i2cset', '-f', '-y', str(bus), str(device), str(register), str(value)]
    status, output = log_os_system(' '.join(cmd), 1)
    #status, output = getstatusoutput_noshell(cmd)
    if status != 0:
        print(f"Error setting register {register} to {value}: {output}")
        return False
    return True

def df810_txfir_set(offset, pre, main, post):
    global TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR

    channel = 1 << offset
    channel_val = f"0x{channel:02x}"

    main_sign = 0x80 if main > 0 else 0x40
    pre_sign, pre_val = (0x40, -pre) if pre <= 0 else (0x00, pre)
    post_sign, post_val = (0x40, -post) if post <= 0 else (0x00, post)

    main_val = f"0x{main | main_sign:02x}"
    pre_val = f"0x{pre_val | pre_sign:02x}"
    post_val = f"0x{post_val | post_sign:02x}"

    register_values = [
        ('0xff', '0x01'),
        ('0xfc', channel_val),
        ('0x3d', '0x80'), # Enable Pre- and Post-cursor FIR
        ('0x3d', '0x80'), # main-cursor sign
        ('0x3f', '0x40'), # post-cursor sign
        ('0x3e', '0x40'), # pre-cursor sign
        ('0x3d', main_val),
        ('0x3f', post_val),
        ('0x3e', pre_val)
    ]

    for register, value in register_values:
        if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, register, value):
            return False

    print(f" Set Ch {offset:02d}: (pre, main, post) = ({pre}, {main}, {post})")

def df810_cdr_bw_set(offset, param1, param2):
    global TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR

    channel = 1 << offset
    channel_val = f"0x{channel:02x}"

    param1_val = f"0x{param1:02x}"
    param2_val = f"0x{param2:02x}"
    register_values = [
        ('0xff', '0x01'),
        ('0xfc', channel_val),
        ('0x1c', param1_val),
        ('0x9e', param2_val),
        ('0x9', '0x8'),
        ('0xa', '0x40'),
    ]

    for register, value in register_values:
        if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, register, value):
            return False

    print(f" Set Ch {offset:02d}: CDR Bandwidth")

def df810_cross_point():
    global TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR

    print("+=======================+")
    print("| Channel | Cross-point |")
    print("+=======================+")

    if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, "0xff", "0x01"):
        return False
    
    for offset in range(8):
        print("|      {:02d} |      B -> A |".format(offset))
        
        channel = 1 << offset
        if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, "0xfc", f"0x{channel:02x}"):
            return False
        time.sleep(0.2)

        register_values = [
            ('0x95', '0x08'),
            ('0x96', '0x00'),
            ('0x96', '0x04'),
            ('0x96', '0x04'),
            ('0x96', '0x06'),
            ('0x96', '0x06'),
            ('0x0a', '0x0c'),
            ('0x0a', '0x00'),
            ('0x79', '0x11')
        ]
        
        for register, value in register_values:
            if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, register, value):
                return False

    print("+=======================+")
    print("Configure cross-point to front-panel SFP28 port...")
    print("------------------------------------------------------")
    print("MAC_TIMUX_TSC_MGMT_TD0 <-> TIMUX_SFP28_P64_SFI_MC_TD0")
    print("MAC_TIMUX_TSC_MGMT_TD2 <-> TIMUX_SFP28_P65_SFI_MC_TD2")
    print("     CPU_TIMUX_10G_TD0 <-> X")
    print("     CPU_TIMUX_10G_TD2 <-> X")
    print("------------------------------------------------------\n")

def config_sfp(dest, speed):
    global TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR
    global CPU, FRONT, S_10G, S_25G

    # Enable df810 MUX
    if not set_i2c_register(TI_MUX_I2C_BUS, "0x72", "0x00", "0x01"):
        return False
    print("Enable df810 MUX\n")
        
    register_values = [
        ('0xfc', '0x01'), # Select channel 0 
        ('0xff', '0x03'), # Bit 1 = 1: Allows customer to write to all channels, 
                          # Bit 0 = 1: Enables SMBus access to the channels specified in register 0xFC.
        ('0x00', '0x04'), # Bit 2 = 1: Reset channel registers to power-up defaults.
        ('0x0a', '0x0c'), # Bit 3 = 1: Enable CDR Reset override.
                          # Bit 2 = 1: CDR Reset override bit.
        ('0x2f', '0x54'), # Bit 5-3  : RATE, 25.78125 Gbps = 0x50
                          # Bit 2 = 1: Enable the PPM to be used as a qualifier when performing Lock Detect.
        ('0x31', '0x40'), # Bit 6-5 = 10: adapt CTLE until optimal, then DFE, then CTLE again.
        ('0x1e', '0xe3'), # Bit 7-5 = 111: Output mode for when the CDR is not locked. 
                          #                For these values to take effect, Reg_0x09[5] must be set to 0, which is
                          #                111: Mute (Default)
                          # bit 1 = 1: Enable DFE taps 3-5. DFE_PD must also be set to 0.
                          # bit 0 = 1: Normal operation. Enable PFD frequency detector. 
        ('0x0a', '0x00')
    ]
    if speed == S_10G:
        register_values[-4] = ('0x2f', '0x04')

    for register, value in register_values:
        if not set_i2c_register(TI_MUX_I2C_BUS, TI_MUX_I2C_ADDR, register, value):
            return False

    if dest == CPU:
        if speed == S_10G:
            df810_txfir_set(0, 0, 17, -2)
            df810_txfir_set(2, 0, 17, -2)
            df810_txfir_set(4, 0, 7, 0)
            df810_txfir_set(6, 0, 7, 0)
            df810_cdr_bw_set(4, 0x24, 0xfc)
            df810_cdr_bw_set(6, 0x24, 0xfc)
    elif dest == FRONT:
        if speed == S_10G:
            df810_txfir_set(1, 0, 15, -3)
            df810_txfir_set(3, 0, 15, -3)
        elif speed == S_25G:
            df810_txfir_set(1, -8, 22, 0)
            df810_txfir_set(3, -8, 22, 0)
        df810_cross_point()

    # Disable df810 MUX
    if not set_i2c_register(TI_MUX_I2C_BUS, "0x72", "0x00", "0x00"):
        return False
    print("Disable df810 MUX\n")
    
    return True

def device_install():
    global FORCE

    for i in range(0,len(mknod)):
        #for pca954x need times to built new i2c buses
        if mknod[i].find('pca954') != -1:
           time.sleep(1)

        status, output = log_os_system(mknod[i], 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    # Select I2C relay channel to MB_EEPROM
    # log_os_system("i2cset -f -a -y 0 0x78 0x00 0x01", 1)
    # time.sleep(0.2)

    ret=eeprom_check()
    if ret==0:
        log_os_system(eeprom_mknod[0], 1)
        time.sleep(0.2)
        exists = os.path.isfile('/sys/bus/i2c/devices/36-0056/eeprom')
        if (exists is False):
            subprocess.call('echo 0x56 > /sys/bus/i2c/devices/i2c-36/delete_device', shell=True)

    for i in range(0,len(sfp_map)):
        if i > osfp_end:
            status, output =log_os_system("echo optoe2 0x50 > /sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/new_device", 1)
        else:
            status, output =log_os_system("echo optoe3 0x50 > /sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/new_device", 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    # Release RESET pin for all OSFP.
    for i in range(0, (osfp_end + 1)):
        status, output = log_os_system("echo 0 > /sys/devices/platform/as9817_32_fpga/module_reset_{}".format(i + 1), 1)
        if status:
            print(output)

    # Disable Low Power Mode for all OSFP.
    for i in range(0, (osfp_end + 1)):
        status, output = log_os_system("echo 0 > /sys/devices/platform/as9817_32_fpga/module_lp_mode_{}".format(i + 1), 1)
        if status:
            print(output)

    # Configure two SFP ports
    config_sfp(FRONT, S_25G)

    # Prevent permission issues between root or admin users for sonic_platform/helper.py
    for i in range(0,len(mkfile)):
        try:
            # Create empty file
            open(mkfile[i], 'a').close()
            os.chmod(mkfile[i], 0o666)
        except OSError:
            print('Failed : creating the file %s.' % (mkfile[i]))
            os.chmod(mkfile[i], 0o666)
            if FORCE == 0:
                return -1

    print("Done device_install")
    return

def device_uninstall():
    global FORCE

    for i in range(0,len(sfp_map)):
        target = "/sys/bus/i2c/devices/i2c-"+str(sfp_map[i])+"/delete_device"
        status, output =log_os_system("echo 0x50 > "+ target, 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    for i in range(len(mknod)):
        target = mknod[-(i+1)]
        temp = target.split()
        del temp[1]
        temp[-1] = temp[-1].replace('new_device', 'delete_device')
        status, output = log_os_system(" ".join(temp), 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    # Deal with for del 0x56 sysfs device
    exists = os.path.isfile('/sys/bus/i2c/devices/36-0056/eeprom')
    if (exists is True):
        target = eeprom_mknod[0] #0x56

    temp = target.split()
    del temp[1]
    temp[-1] = temp[-1].replace('new_device', 'delete_device')
    status, output = log_os_system(" ".join(temp), 1)
    if status:
        print(output)
        if FORCE == 0:
           return status

    for i in range(0,len(mkfile)):
        status, output = log_os_system('rm -f ' + mkfile[i], 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

    return

def system_ready():
    if driver_check() == False:
        return False
    if not device_exist():
        return False
    return True

PLATFORM_ROOT_PATH = '/usr/share/sonic/device'
PLATFORM_API2_WHL_FILE_PY3 ='sonic_platform-1.0-py3-none-any.whl'
def do_sonic_platform_install():
    device_path = "{}{}{}{}".format(PLATFORM_ROOT_PATH, '/x86_64-accton_', PROJECT_NAME, '-r0')
    SONIC_PLATFORM_BSP_WHL_PKG_PY3 = "/".join([device_path, PLATFORM_API2_WHL_FILE_PY3])

    #Check API2.0 on py whl file
    status, output = log_os_system("pip3 show sonic-platform > /dev/null 2>&1", 0)
    if status:
        if os.path.exists(SONIC_PLATFORM_BSP_WHL_PKG_PY3):
            status, output = log_os_system("pip3 install "+ SONIC_PLATFORM_BSP_WHL_PKG_PY3, 1)
            if status:
                print("Error: Failed to install {}".format(PLATFORM_API2_WHL_FILE_PY3))
                return status
            else:
                print("Successfully installed {} package".format(PLATFORM_API2_WHL_FILE_PY3))
        else:
            print('{} is not found'.format(PLATFORM_API2_WHL_FILE_PY3))
    else:
        print('{} has installed'.format(PLATFORM_API2_WHL_FILE_PY3))

    return

def do_sonic_platform_clean():
    status, output = log_os_system("pip3 show sonic-platform > /dev/null 2>&1", 0)
    if status:
        print('{} does not install, not need to uninstall'.format(PLATFORM_API2_WHL_FILE_PY3))

    else:
        status, output = log_os_system("pip3 uninstall sonic-platform -y", 0)
        if status:
            print('Error: Failed to uninstall {}'.format(PLATFORM_API2_WHL_FILE_PY3))
            return status
        else:
            print('{} is uninstalled'.format(PLATFORM_API2_WHL_FILE_PY3))

    return

device_path = f"{PLATFORM_ROOT_PATH}/x86_64-accton_{PROJECT_NAME}-r0"
apply_ais800_cmds = [
    f"sed -i 's/\"name\":\ \"AS9817-32O\"/\"name\":\ \"AIS800-32O\"/g' {device_path}/platform.json",
    f"cp -f {device_path}/platform_components.json.ais800 {device_path}/platform_components.json",
    f"cp -f {device_path}/pcie.yaml.ais800 {device_path}/pcie.yaml",
]
apply_as9817_cmds = [
    f"sed -i 's/\"name\":\ \"AIS800-32O\"/\"name\":\ \"AS9817-32O\"/g' {device_path}/platform.json",
    f"cp -f {device_path}/platform_components.json.as9817 {device_path}/platform_components.json",
    f"cp -f {device_path}/pcie.yaml.as9817 {device_path}/pcie.yaml",
]
apply_cmd_sets = {
    0x00 : apply_as9817_cmds, # OSFP
    0x01 : apply_as9817_cmds, # QDD
    0x02 : apply_ais800_cmds, # OSFP DC-SCM  ==> AIS800-32O
    0x03 : apply_ais800_cmds  # QDD DC-SCM   ==> AIS800-32D
}

def get_pcb_id():
    id = None
    status, output = getstatusoutput_noshell("i2cget -f -y 0 0x60 0x00".split())
    if status == 0:
        try:
            id = int(output, 16)
        except Exception as e:
            print(e)
            pass

    return id

def apply_product_conf():
    pcb_id = get_pcb_id()
    if pcb_id is None:
        print("Invalid PCB ID.")
        return

    apply_cmds = apply_cmd_sets.get((pcb_id >> 2) & 0x03, [])
    if apply_cmds == []:
        print("No matching commands found for the PCB ID.")
        return

    if apply_cmds == apply_ais800_cmds:
        print("Apply AIS800 Configuration")
    elif apply_cmds == apply_as9817_cmds:
        print("Apply AS9817 Configuration")

    for cmd in apply_cmds:
        status, output = log_os_system(cmd, 1)
        if status:
            print(output)
            if FORCE == 0:
                return status

def do_install():
    print("Checking system....")
    if driver_check() == False:
        print("No driver, installing....")
        status = driver_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print(PROJECT_NAME.upper()+" drivers detected....")

    if not device_exist():
        print("No device, installing....")
        status = device_install()
        if status:
            if FORCE == 0:
                return  status
    else:
        print(PROJECT_NAME.upper()+" devices detected....")

    # Turn off LOC LED if needed
    log_os_system("echo 0 > /sys/devices/platform/as9817_32_led/led_loc", 1)

    # Chnage all fan_pwm to 67%
    for filename in glob.glob("/sys/devices/platform/as9817_32_fan/hwmon/*/fan*_pwm"):
        try:
            with open(filename, 'w') as fd:
                fd.write(str(FAN_PWM))
        except IOError as e:
            pass

    # apply_product_conf()

    do_sonic_platform_install()

    return

def do_uninstall():
    print("Checking system....")
    if not device_exist():
        print(PROJECT_NAME.upper() +" has no device installed....")
    else:
        print("Removing device....")
        status = device_uninstall()
        if status:
            if FORCE == 0:
                return  status

    if driver_check()== False :
        print(PROJECT_NAME.upper() +" has no driver installed....")
    else:
        print("Removing installed driver....")
        status = driver_uninstall()
        if status:
            if FORCE == 0:
                return  status

    do_sonic_platform_clean()

    return

def device_exist():
    ret1, log = log_os_system("ls "+i2c_prefix+"*0070", 0)
    ret2, log = log_os_system("ls "+i2c_prefix+"i2c-2", 0)
    return not(ret1 or ret2)

THRESHOLD_RANGE_LOW = 30.0
THRESHOLD_RANGE_HIGH = 110.0
# Code to initialize chassis object
init_chassis_code = \
    "import sonic_platform.platform\n"\
    "platform = sonic_platform.platform.Platform()\n"\
    "chassis = platform.get_chassis()\n\n"

# Looking for thermal
looking_for_thermal_code = \
    "thermal = None\n"\
    "all_thermals = chassis.get_all_thermals()\n"\
    "for psu in chassis.get_all_psus():\n"\
    "    all_thermals += psu.get_all_thermals()\n"\
    "for tmp in all_thermals:\n"\
    "    if '{}' == tmp.get_name():\n"\
    "        thermal = tmp\n"\
    "        break\n"\
    "if thermal == None:\n"\
    "    print('{} not found!')\n"\
    "    exit(1)\n\n"

def avaliable_thermals():
    global init_chassis_code

    get_all_thermal_name_code = \
        "thermal_list = []\n"\
        "all_thermals = chassis.get_all_thermals()\n"\
        "for psu in chassis.get_all_psus():\n"\
        "    all_thermals += psu.get_all_thermals()\n"\
        "for tmp in all_thermals:\n"\
        "    thermal_list.append(tmp.get_name())\n"\
        "print(str(thermal_list)[1:-1])\n"

    all_code = "{}{}".format(init_chassis_code, get_all_thermal_name_code)

    status, output = getstatusoutput_noshell(["docker", "exec", "pmon", "python3", "-c", all_code])
    if status != 0:
        return ""
    return output

def restricted_float(x):
    global THRESHOLD_RANGE_LOW, THRESHOLD_RANGE_HIGH

    try:
        x = float(x)
    except ValueError:
        raise argparse.ArgumentTypeError("%r not a floating-point literal" % (x,))

    if x < THRESHOLD_RANGE_LOW or x > THRESHOLD_RANGE_HIGH:
        raise argparse.ArgumentTypeError("%r not in range [%.1f ~ %.1f]" % 
                                         (x, THRESHOLD_RANGE_LOW, THRESHOLD_RANGE_HIGH))

    return x

def get_high_threshold(name):
    global init_chassis_code, looking_for_thermal_code

    get_high_threshold_code = \
        "try:\n"\
        "    print(thermal.get_high_threshold())\n"\
        "    exit(0)\n"\
        "except NotImplementedError:\n"\
        "    print('Not implement the get_high_threshold method!')\n"\
        "    exit(1)"

    all_code = "{}{}{}".format(init_chassis_code, looking_for_thermal_code.format(name, name),
                               get_high_threshold_code)

    status, output = getstatusoutput_noshell(["docker", "exec", "pmon", "python3", "-c", all_code])
    if status == 1:
        return None

    return float(output)

def get_high_crit_threshold(name):
    global init_chassis_code, looking_for_thermal_code

    get_high_crit_threshold_code = \
        "try:\n"\
        "    print(thermal.get_high_critical_threshold())\n"\
        "    exit(0)\n"\
        "except NotImplementedError:\n"\
        "    print('Not implement the get_high_critical_threshold method!')\n"\
        "    exit(1)"

    all_code = "{}{}{}".format(init_chassis_code, looking_for_thermal_code.format(name, name),
                               get_high_crit_threshold_code)

    status, output = getstatusoutput_noshell(["docker", "exec", "pmon", "python3", "-c", all_code])
    if status == 1:
        return None

    return float(output)

def do_sfp():
    global CPU, FRONT, S_10G, S_25G

    if args.cpu:
        config_sfp(CPU, S_10G)
    elif args.front10:
        config_sfp(FRONT, S_10G)
    elif args.front25:
        config_sfp(FRONT, S_25G)

def do_threshold():
    global args, init_chassis_code, looking_for_thermal_code

    if args.list:
        print("Thermals: " + avaliable_thermals())
        return

    if args.thermal is None:
        print("The following arguments are required: -t")
        return

    set_threshold_code = ""
    if args.high_threshold is not None:
        if args.high_crit_threshold is not None and \
            args.high_threshold >= args.high_crit_threshold:
           print("Invalid Threshold!(High threshold can not be more than " \
                 "or equal to high critical threshold.)")
           exit(1)

        high_crit = get_high_crit_threshold(args.thermal)
        if high_crit is not None and \
           args.high_threshold >= high_crit:
           print("Invalid Threshold!(High threshold can not be more than " \
                 "or equal to high critical threshold.)")
           exit(1)

        set_threshold_code += \
            "try:\n"\
            "    if thermal.set_high_threshold({}) is False:\n"\
            "        print('{}: set_high_threshold failure!')\n"\
            "        exit(1)\n"\
            "except NotImplementedError:\n"\
            "    print('Not implement the set_high_threshold method!')\n"\
            "print('Apply the new high threshold successfully.')\n"\
            "\n".format(args.high_threshold, args.thermal)

    if args.high_crit_threshold is not None:
        high = get_high_threshold(args.thermal)
        if high is not None and \
            args.high_crit_threshold <= high:
            print("Invalid Threshold!(High critical threshold can not " \
                  "be less than or equal to high threshold.)")
            exit(1)

        set_threshold_code += \
            "try:\n"\
            "    if thermal.set_high_critical_threshold({}) is False:\n"\
            "        print('{}: set_high_critical_threshold failure!')\n"\
            "        exit(1)\n"\
            "except NotImplementedError:\n"\
            "    print('Not implement the set_high_critical_threshold method!')\n"\
            "print('Apply the new high critical threshold successfully.')\n"\
            "\n".format(args.high_crit_threshold, args.thermal)

    if set_threshold_code == "":
        return

    all_code = "{}{}{}".format(init_chassis_code, looking_for_thermal_code.format(args.thermal, args.thermal), set_threshold_code)

    status, output = getstatusoutput_noshell(["docker", "exec", "pmon", "python3", "-c", all_code])
    print(output)

if __name__ == "__main__":
    main()

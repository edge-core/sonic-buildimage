#!/usr/bin/env python
#

import os
import time
import syslog
import re
from sonic_sfp.bcmshell import bcmshell

# =====================================================================
#  global variable init
# =====================================================================

# define data ram address
PORT_DATA_OFFSET_ADDR   = 0xA0
PORT_DATA_START_ADDR    = 0xF2
TOTAL_SCAN_BITS_ADDR    = 0xF4
SYNC_START_LEN_ADDR     = 0xF6
SYNC_STOP_LEN_ADDR      = 0xF8
# bit streaming rule for CPLD decode
TOTAL_SCAN_BITS         = None
SYNC_S                  = None
SYNC_P                  = None
# define port data for bit streaming
BIT_LINK                = None
BIT_FAULT               = None
BIT_TX                  = None
BIT_RX                  = None
BIT_SPEED0              = None
BIT_SPEED1              = None
# define port speed
SPEED_100G              = 100
SPEED_40G               = 40
SPEED_25G               = 25
SPEED_10G               = 10
# the amount of LED processor
AMOUNT_LED_UP           = None
# define board type
INV_REDWOOD             = "SONiC-Inventec-d7032-100"
INV_CYPRESS             = "SONiC-Inventec-d7054"
INV_SEQUOIA             = ""
BOARD_TPYE              = ""
EAGLE_CORE              = []

PORT_LIST               = []

# port status that is auto update by chip in data ram
# there are two byte to indicate each port status
'''
RX              equ     0x0     ; received packet
TX              equ     0x1     ; transmitted packet
COLL            equ     0x2     ; collision indicator
SPEED_C         equ     0x3     ; 100 Mbps
SPEED_M         equ     0x4     ; 1000 Mbps
DUPLEX          equ     0x5     ; half/full duplex
FLOW            equ     0x6     ; flow control capable
LINKUP          equ     0x7     ; link down/up status
LINKEN          equ     0x8     ; link disabled/enabled status
ZERO            equ     0xE     ; always 0
ONE             equ     0xF     ; always 1
'''
STATUS_ENABLE           = 1<<0
STATUS_RX               = 1<<0
STATUS_TX               = 1<<1

# object is to execute bcm shell command
BCM_SHELL = None



# =====================================================================
#  class object
# =====================================================================
class Led():

    up  = None
    pfw = None

    def __init__(self, led_number, program_fw):
        self.up = led_number
        self.pfw = program_fw

    def led_start(self):
        BCM_SHELL.cmd("led {0} start".format(self.up))
        syslog.syslog(syslog.LOG_INFO, "Start Led({0})".format(self.up))

    def led_stop(self):
        BCM_SHELL.cmd("led {0} stop".format(self.up))
        syslog.syslog(syslog.LOG_INFO, "Stop Led({0})".format(self.up))

    def load_prog(self):
        BCM_SHELL.cmd("led {0} prog {1}".format(self.up, self.pfw))
        syslog.syslog(syslog.LOG_INFO, "Load Led({0}) program firmware".format(self.up))

    def write_port_data(self, addr, data):
        BCM_SHELL.cmd("setreg CMIC_LEDUP{0}_DATA_RAM({1}) {2}".format(self.up, addr, data))
        #syslog.syslog(syslog.LOG_DEBUG, "Write Led({0}) data_ram({1}): {2}".format(self.up, addr, data))

    def read_data_ram(self, offset):
        return_string = BCM_SHELL.run("getreg CMIC_LEDUP{0}_DATA_RAM({1})".format(self.up, offset))
        for line in return_string.split("\n"):
            re_obj = re.search(r"\<DATA\=(?P<data>.+)\>",line)
            if re_obj is not None:
                #syslog.syslog(syslog.LOG_DEBUG, "Read Led({0}) data_ram({1}): {2}".format(self.up, offset, re_obj.group("data")))
                return int(re_obj.group("data"), 16)

        return None


# =====================================================================
#  Function
# =====================================================================
def _remap_registers():

    fp = open('/usr/share/sonic/device/x86_64-inventec_d7032q28b-r0/led_proc_init.soc', "r")
    content = fp.readlines()
    fp.close()
    err = False

    for line in content:
        try:
            BCM_SHELL.cmd(line.rstrip())
        except Exception, e:
            err = True
            syslog.syslog(syslog.LOG_ERR, "remap register abnormal: {0}".format(str(e)))

    if not err:
        pass
        #syslog.syslog(syslog.LOG_DEBUG, "remap Led registers successfully")



def _update_port_list():

    global PORT_LIST
    PORT_LIST = []
    number = 0
    count = 0

    content = BCM_SHELL.run("ps")
    for line in content.split("\n"):
        re_obj = re.search(r"(?P<port_name>(xe|ce)\d+)\(\s*(?P<bcm_id>\d+)\)\s+(?P<link>(up|down|!ena)).+\s+(?P<speed>\d+)G",line)
        if re_obj is not None:
            if int(re_obj.group("bcm_id")) not in EAGLE_CORE:
                PORT_LIST.append({"port_id":number, "name":re_obj.group("port_name"), "bcm_id":int(re_obj.group("bcm_id")), "link":re_obj.group("link"), "speed":int(re_obj.group("speed"))})
                number += 1

    content = BCM_SHELL.run("led status")
    for line in content.split("\n"):
        re_obj = re.search(r"(?P<bcm_id>\d+).+(?P<led_up>\d)\:(?P<offset>\d+)",line)
        if re_obj is not None:
            if int(re_obj.group("bcm_id")) not in EAGLE_CORE:
                PORT_LIST[count]["led_up"] = int(re_obj.group("led_up"))
                PORT_LIST[count]["offset"] = int(re_obj.group("offset"))
                count += 1

    if number is not count:
        PORT_LIST = []
        syslog.syslog(syslog.LOG_ERR, "The amount of port is not match")
    else:
        pass
        #syslog.syslog(syslog.LOG_DEBUG, "update port list successfully")



def _lookup_led_index(p):

    index = 0
    for port in PORT_LIST:
        if p["bcm_id"] == port["bcm_id"]:
            break
        if p["led_up"] == port["led_up"]:
            index += 1
    return index + PORT_DATA_OFFSET_ADDR



def _led_init():

    global BOARD_TPYE
    global AMOUNT_LED_UP
    global BIT_LINK
    global BIT_FAULT
    global BIT_TX
    global BIT_RX
    global BIT_SPEED0
    global BIT_SPEED1
    global EAGLE_CORE
    global TOTAL_SCAN_BITS
    global SYNC_S
    global SYNC_P

    cmd = "uname -n"
    platform = os.popen(cmd).read()

    if platform.rstrip() == INV_REDWOOD:
        BOARD_TPYE      = "inventec_d7032q28b"
        AMOUNT_LED_UP   = 2
        BIT_RX          = 1<<0  #0x01
        BIT_TX          = 1<<1  #0x02
        BIT_SPEED0      = 1<<3  #0x08
        BIT_SPEED1      = 1<<4  #0x10
        BIT_FAULT       = 1<<6  #0x40
        BIT_LINK        = 1<<7  #0x80
        TOTAL_SCAN_BITS = 32*1*4
        SYNC_S          = 15
        SYNC_P          = 3
        EAGLE_CORE      = [66, 100]
        _remap_registers()

    elif platform.rstrip() == INV_CYPRESS:
        BOARD_TPYE      = "inventec_d7054q28b"
        AMOUNT_LED_UP   = 2
        BIT_LINK        = 1<<0  #0x01
        BIT_FAULT       = 1<<1  #0x02
        BIT_SPEED0      = 1<<2  #0x04
        EAGLE_CORE      = [66, 100]

    elif platform.rstrip() == INV_SEQUOIA:
        BOARD_TPYE = "inventec_d7264q28b"
        AMOUNT_LED_UP = 4

    else:
        BOARD_TPYE = "not found"

    syslog.syslog(syslog.LOG_INFO, "Device: {0}".format(BOARD_TPYE))
    #syslog.syslog(syslog.LOG_DEBUG, "led_amount: {0}".format(AMOUNT_LED_UP))



if __name__ == "__main__":

    waitSyncd = True
    retryCount = 0
    syslog.openlog("led_proc", syslog.LOG_PID, facility=syslog.LOG_DAEMON)

    while waitSyncd:
        try:
            BCM_SHELL = bcmshell()
            waitSyncd = False
        except Exception, e:
            syslog.syslog(syslog.LOG_WARNING, "{0}, Retry times({1})".format(str(e),retryCount))
            retryCount += 1
        time.sleep(5)


    _led_init()
    led_obj = []
    for idx in range(AMOUNT_LED_UP):
        led_obj.append(Led(idx, ""))
        #syslog.syslog(syslog.LOG_DEBUG, "create object led({0}) successfully".format(idx))

        if BOARD_TPYE == "inventec_d7032q28b":
            led_obj[idx].write_port_data(PORT_DATA_START_ADDR, PORT_DATA_OFFSET_ADDR)
            led_obj[idx].write_port_data(TOTAL_SCAN_BITS_ADDR, TOTAL_SCAN_BITS)
            led_obj[idx].write_port_data(SYNC_START_LEN_ADDR, SYNC_S)
            led_obj[idx].write_port_data(SYNC_STOP_LEN_ADDR, SYNC_P)


    reset_sec = 2
    count_down = 0
    queue_active = []
    port_data = None
    while True:
        if count_down == 0:
            queue_active = []
            _update_port_list()
            for port in PORT_LIST:
                if port["link"] == "up":
                    queue_active.append(port)
                else:
                    port_data = 0
                    # redwood bit streaming for CPLD decode is only use led up0
                    led_obj[0].write_port_data(PORT_DATA_OFFSET_ADDR + port["port_id"], port_data)
            count_down = reset_sec
        else:
            for port in queue_active:
                port_data = 0

                if BOARD_TPYE == "inventec_d7032q28b":
                    port_data |= BIT_LINK
                    addr = 2*(port["offset"]-1)
                    byte1 = led_obj[port["led_up"]].read_data_ram(addr)
                    byte2 = led_obj[port["led_up"]].read_data_ram(addr+1)
                    if byte1&STATUS_RX:
                        port_data |= BIT_RX
                    if byte1&STATUS_TX:
                        port_data |= BIT_TX
                    if port["speed"] == SPEED_100G:
                        port_data |= BIT_SPEED0
                        port_data |= BIT_SPEED1
                    elif port["speed"] == SPEED_40G:
                        port_data |= BIT_SPEED1
                    elif port["speed"] == SPEED_25G:
                        port_data |= BIT_SPEED0
                    else:
                        pass

                    # redwood bit streaming for CPLD decode is only use led up0
                    led_obj[0].write_port_data(PORT_DATA_OFFSET_ADDR + port["port_id"], port_data)
                    continue

                elif BOARD_TPYE == "inventec_d7054q28b":
                    if port["speed"] != SPEED_100G and port["speed"] != SPEED_25G:
                        port_data |= BIT_SPEED0

                led_index = _lookup_led_index(port)
                led_obj[port["led_up"]].write_port_data(led_index, port_data)

            time.sleep(0.5)
            count_down -= 1

    syslog.closelog()


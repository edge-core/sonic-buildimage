#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import click
import os
import time
import traceback
import glob
from rgutil.logutil import Logger
from ragileutil import wait_docker

from ragileconfig import (
    MONITOR_CONST,
    FANCTROLDEBUG,
    MONITOR_FANS_LED,
    DEV_LEDS,
    MONITOR_PSU_STATUS,
    MONITOR_SYS_PSU_LED,
    MONITOR_DEV_STATUS,
    MONITOR_FAN_STATUS,
    MONITOR_DEV_STATUS_DECODE,
    MONITOR_SYS_FAN_LED,
    MONITOR_SYS_LED,
    fanloc,
)

from ragileutil import (
    rgi2cget,
    get_mac_temp_sysfs,
    get_mac_temp,
    write_sysfs_value,
    get_sysfs_value,
    strtoint,
    rgi2cset,
)


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

DEBUG_COMMON = 0x01
DEBUG_LEDCONTROL = 0x02
DEBUG_FANCONTROL = 0x04

LOG_PREFIX = "FANCONTROL"
logger = Logger(LOG_PREFIX, syslog=True, dbg_mask=FANCTROLDEBUG)


class AliasedGroup(click.Group):
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail("Too many matches: %s" % ", ".join(sorted(matches)))


class FanControl(object):
    critnum = 0

    def __init__(self):
        self._normal_fans = 0
        self._normal_psus = 0
        self._intemp = -100.0
        self._mac_aver = -100.0
        self._mac_max = -100.0
        # previous temperature
        self._pre_intemp = -100
        self._outtemp = -100
        self._boardtemp = -100
        self._cputemp = -1000

    @property
    def normal_fans(self):
        return self._normal_fans

    @property
    def normal_psus(self):
        return self._normal_psus

    @property
    def cputemp(self):
        return self._cputemp

    @property
    def intemp(self):
        return self._intemp

    @property
    def outtemp(self):
        return self._outtemp

    @property
    def boardtemp(self):
        return self._boardtemp

    @property
    def mac_aver(self):
        return self._mac_aver

    @property
    def preIntemp(self):
        return self._pre_intemp

    @property
    def mac_max(self):
        return self._mac_max

    def sortCallback(self, element):
        return element["id"]

    def gettemp(self, ret):
        u"""get inlet, outlet, hot-point and cpu temperature"""
        temp_conf = MONITOR_DEV_STATUS.get("temperature", None)

        if temp_conf is None:
            logger.error("gettemp: config error")
            return False
        for item_temp in temp_conf:
            try:
                retval = ""
                rval = None
                name = item_temp.get("name")
                location = item_temp.get("location")
                if name == "cpu":
                    L = []
                    for dirpath, dirnames, filenames in os.walk(location):
                        for file in filenames:
                            if file.endswith("input"):
                                L.append(os.path.join(dirpath, file))
                        L = sorted(L, reverse=False)
                    for i in range(len(L)):
                        nameloc = "%s/temp%d_label" % (location, i + 1)
                        valloc = "%s/temp%d_input" % (location, i + 1)
                        with open(nameloc, "r") as fd1:
                            retval2 = fd1.read()
                        with open(valloc, "r") as fd2:
                            retval3 = fd2.read()
                        ret_t = {}
                        ret_t["name"] = retval2.strip()
                        ret_t["value"] = float(retval3) / 1000
                        ret.append(ret_t)
                        logger.debug(
                            DEBUG_COMMON,
                            "gettemp %s : %f" % (ret_t["name"], ret_t["value"]),
                        )
                else:
                    locations = glob.glob(location)
                    with open(locations[0], "r") as fd1:
                        retval = fd1.read()
                    rval = float(retval) / 1000
                    ret_t = {}
                    ret_t["name"] = name
                    ret_t["value"] = rval
                    ret.append(ret_t)
                    logger.debug(
                        DEBUG_COMMON,
                        "gettemp %s : %f" % (ret_t["name"], ret_t["value"]),
                    )
            except Exception as e:
                logger.error("gettemp error:name:%s" % name)
                logger.error(str(e))
        return True

    def checkslot(self, ret):
        u"""get slot present status"""
        slots_conf = MONITOR_DEV_STATUS.get("slots", None)
        slotpresent = MONITOR_DEV_STATUS_DECODE.get("slotpresent", None)

        if slots_conf is None or slotpresent is None:
            return False
        for item_slot in slots_conf:
            totalerr = 0
            try:
                ret_t = {}
                ret_t["id"] = item_slot.get("name")
                ret_t["status"] = ""
                gettype = item_slot.get("gettype")
                presentbit = item_slot.get("presentbit")
                if gettype == "io":
                    io_addr = item_slot.get("io_addr")
                    val = io_rd(io_addr)
                    if val is not None:
                        retval = val
                    else:
                        totalerr -= 1
                        logger.error(
                            " %s  %s" % (item_slot.get("name"), "lpc read failed"),
                        )
                else:
                    bus = item_slot.get("bus")
                    loc = item_slot.get("loc")
                    offset = item_slot.get("offset")
                    ind, val = rgi2cget(bus, loc, offset)
                    if ind == True:
                        retval = val
                    else:
                        totalerr -= 1
                        logger.error(
                            " %s  %s" % (item_slot.get("name"), "i2c read failed"),
                        )
                if totalerr < 0:
                    ret_t["status"] = "NOT OK"
                    ret.append(ret_t)
                    continue
                val_t = (int(retval, 16) & (1 << presentbit)) >> presentbit
                logger.debug(
                    DEBUG_COMMON,
                    "%s present:%s" % (item_slot.get("name"), slotpresent.get(val_t)),
                )
                if val_t != slotpresent.get("okval"):
                    ret_t["status"] = "ABSENT"
                else:
                    ret_t["status"] = "PRESENT"
            except Exception as e:
                ret_t["status"] = "NOT OK"
                totalerr -= 1
                logger.error("checkslot error")
                logger.error(str(e))
            ret.append(ret_t)
        return True

    def checkpsu(self, ret):
        u"""get  psu status present, output and warning"""
        psus_conf = MONITOR_DEV_STATUS.get("psus", None)
        psupresent = MONITOR_DEV_STATUS_DECODE.get("psupresent", None)
        psuoutput = MONITOR_DEV_STATUS_DECODE.get("psuoutput", None)
        psualert = MONITOR_DEV_STATUS_DECODE.get("psualert", None)

        if psus_conf is None or psupresent is None or psuoutput is None:
            logger.error("checkpsu: config error")
            return False
        for item_psu in psus_conf:
            totalerr = 0
            try:
                ret_t = {}
                ret_t["id"] = item_psu.get("name")
                ret_t["status"] = ""
                gettype = item_psu.get("gettype")
                presentbit = item_psu.get("presentbit")
                statusbit = item_psu.get("statusbit")
                alertbit = item_psu.get("alertbit")
                if gettype == "io":
                    io_addr = item_psu.get("io_addr")
                    val = io_rd(io_addr)
                    if val is not None:
                        retval = val
                    else:
                        totalerr -= 1
                        logger.error(
                            " %s  %s" % (item_psu.get("name"), "lpc read failed"),
                        )
                else:
                    bus = item_psu.get("bus")
                    loc = item_psu.get("loc")
                    offset = item_psu.get("offset")
                    ind, val = rgi2cget(bus, loc, offset)
                    if ind == True:
                        retval = val
                    else:
                        totalerr -= 1
                        logger.error(
                            " %s  %s" % (item_psu.get("name"), "i2c read failed"),
                        )
                if totalerr < 0:
                    ret_t["status"] = "NOT OK"
                    ret.append(ret_t)
                    continue
                val_t = (int(retval, 16) & (1 << presentbit)) >> presentbit
                val_status = (int(retval, 16) & (1 << statusbit)) >> statusbit
                val_alert = (int(retval, 16) & (1 << alertbit)) >> alertbit
                logger.debug(
                    DEBUG_COMMON,
                    "%s present:%s output:%s alert:%s"
                    % (
                        item_psu.get("name"),
                        psupresent.get(val_t),
                        psuoutput.get(val_status),
                        psualert.get(val_alert),
                    ),
                )
                if (
                    val_t != psupresent.get("okval")
                    or val_status != psuoutput.get("okval")
                    or val_alert != psualert.get("okval")
                ):
                    totalerr -= 1
            except Exception as e:
                totalerr -= 1
                logger.error("checkpsu error")
                logger.error(str(e))
            if totalerr < 0:
                ret_t["status"] = "NOT OK"
            else:
                ret_t["status"] = "OK"
            ret.append(ret_t)
        return True

    def checkfan(self, ret):
        u"""get fan status present and roll"""
        fans_conf = MONITOR_DEV_STATUS.get("fans", None)
        fanpresent = MONITOR_DEV_STATUS_DECODE.get("fanpresent", None)
        fanroll = MONITOR_DEV_STATUS_DECODE.get("fanroll", None)

        if fans_conf is None or fanpresent is None or fanroll is None:
            logger.error("checkfan: config error")
            return False
        for item_fan in fans_conf:
            totalerr = 0
            try:
                ret_t = {}
                ret_t["id"] = item_fan.get("name")
                ret_t["status"] = ""
                presentstatus = item_fan.get("presentstatus")
                presentbus = presentstatus.get("bus")
                presentloc = presentstatus.get("loc")
                presentaddr = presentstatus.get("offset")
                presentbit = presentstatus.get("bit")
                ind, val = rgi2cget(presentbus, presentloc, presentaddr)
                if ind == True:
                    val_t = (int(val, 16) & (1 << presentbit)) >> presentbit
                    logger.debug(
                        DEBUG_COMMON,
                        "checkfan:%s present status:%s"
                        % (item_fan.get("name"), fanpresent.get(val_t)),
                    )
                    if val_t != fanpresent.get("okval"):
                        ret_t["status"] = "ABSENT"
                        ret.append(ret_t)
                        continue
                else:
                    logger.error(
                        "checkfan: %s get present status error." % item_fan.get("name"),
                    )
                motors = item_fan.get("rollstatus")
                for motor in motors:
                    statusbus = motor.get("bus", None)
                    statusloc = motor.get("loc", None)
                    statusaddr = motor.get("offset", None)
                    statusbit = motor.get("bit", None)
                    ind, val = rgi2cget(statusbus, statusloc, statusaddr)
                    if ind == True:
                        val_t = (int(val, 16) & (1 << statusbit)) >> statusbit
                        logger.debug(
                            DEBUG_COMMON,
                            "checkfan:%s roll status:%s"
                            % (motor.get("name"), fanroll.get(val_t)),
                        )
                        if val_t != fanroll.get("okval"):
                            totalerr -= 1
                    else:
                        totalerr -= 1
                        logger.error("checkfan: %s " % item_fan.get("name"))
                        logger.error("get %s status error." % motor["name"])
            except Exception as e:
                totalerr -= 1
                logger.error("checkfan error")
                logger.error(str(e))
            if totalerr < 0:
                ret_t["status"] = "NOT OK"
            else:
                ret_t["status"] = "OK"
            ret.append(ret_t)
        return True

    def get_curr_speed(self):
        try:
            loc = fanloc[0].get("location", "")
            sped = get_sysfs_value(loc)
            value = strtoint(sped)
            return value
        except Exception as e:
            logger.error("%%policy: get current speedlevel error")
            logger.error(str(e))
            return None

    # guarantee the speed is lowest when speed lower than lowest value after speed-adjustment
    def check_curr_speed(self):
        logger.debug(
            DEBUG_FANCONTROL,
            "%%policy: guarantee the lowest speed after speed-adjustment",
        )
        value = self.get_curr_speed()
        if value is None or value == 0:
            raise Exception("%%policy: get_curr_speed None")
        elif value < MONITOR_CONST.MIN_SPEED:
            self.set_fan_speed(MONITOR_CONST.MIN_SPEED)

    def set_fan_speed(self, level):
        if level >= MONITOR_CONST.MAX_SPEED:
            level = MONITOR_CONST.MAX_SPEED
        for item in fanloc:
            try:
                loc = item.get("location", "")
                # write_sysfs_value(loc, "0x%02x" % level)
                # pddf support dicimal number
                write_sysfs_value(loc, "%d" % level)
            except Exception as e:
                logger.error(str(e))
                logger.error("%%policy: config fan runlevel error")
        self.check_curr_speed()  # guaranteed minimum

    def set_fan_max_speed(self):
        try:
            self.set_fan_speed(MONITOR_CONST.MAX_SPEED)
        except Exception as e:
            logger.error("%%policy:set_fan_max_speed failed")
            logger.error(str(e))

    def detect_fan_status(self):
        """
        fan status check , max speed if fan error
        """
        if self.normal_fans < MONITOR_CONST.FAN_TOTAL_NUM:
            logger.warn(
                "%%DEV_MONITOR-FAN: Normal fan number: %d" % (self.normal_fans),
            )
            self.set_fan_max_speed()
            return False
        return True

    def set_fan_attr(self, val):
        u"""set status of each fan"""
        for item in val:
            fanid = item.get("id")
            fanattr = fanid + "status"
            fanstatus = item.get("status")
            setattr(FanControl, fanattr, fanstatus)
            logger.debug(
                DEBUG_COMMON, "fanattr:%s,fanstatus:%s" % (fanattr, fanstatus),
            )

    def fan_present_num(self, cur_fan_status):
        fanoknum = 0
        for item in cur_fan_status:
            if item["status"] == "OK":
                fanoknum += 1
        self._normal_fans = fanoknum
        logger.debug(DEBUG_COMMON, "normal_fans = %d" % self._normal_fans)

    def get_fan_status(self):
        try:
            cur_fan_status = []
            ret = self.checkfan(cur_fan_status)
            if ret == True:
                self.set_fan_attr(cur_fan_status)
                self.fan_present_num(cur_fan_status)
                logger.debug(DEBUG_COMMON, "%%policy:get_fan_status success")
                return 0
        except AttributeError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
        return -1

    def normal_psu_num(self, curPsuStatus):
        psuoknum = 0
        for item in curPsuStatus:
            if item.get("status") == "OK":
                psuoknum += 1
        self._normal_psus = psuoknum
        logger.debug(DEBUG_COMMON, "normal_psus = %d" % self._normal_psus)

    def get_psu_status(self):
        try:
            curPsuStatus = []
            ret = self.checkpsu(curPsuStatus)
            if ret == True:
                self.normal_psu_num(curPsuStatus)
                logger.debug(DEBUG_COMMON, "%%policy:get_psu_status success")
                return 0
        except AttributeError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
        return -1

    def get_monitor_temp(self, temp):
        for item in temp:
            if item.get("name") == "lm75in":
                self._intemp = item.get("value", self._intemp)
            if item.get("name") == "lm75out":
                self._outtemp = item.get("value", self._outtemp)
            if item.get("name") == "lm75hot":
                self._boardtemp = item.get("value", self._boardtemp)
            if item.get("name") == "Physical id 0":
                self._cputemp = item.get("value", self._cputemp)
        logger.debug(
            DEBUG_COMMON,
            "intemp:%f, outtemp:%f, boadrtemp:%f, cputemp:%f"
            % (self._intemp, self._outtemp, self._boardtemp, self._cputemp),
        )

    def get_temp_status(self):
        try:
            monitortemp = []
            ret = self.gettemp(monitortemp)
            if ret == True:
                self.get_monitor_temp(monitortemp)
                logger.debug(DEBUG_COMMON, "%%policy:get_temp_status success")
                return 0
        except AttributeError as e:
            logger.error(str(e))
        except Exception as e:
            logger.error(str(e))
        return -1

    def get_mac_status_bcmcmd(self):
        try:
            if wait_docker(timeout=0) == True:
                sta, ret = get_mac_temp()
                if sta == True:
                    self._mac_aver = float(ret.get("average", self._mac_aver))
                    self._mac_max = float(ret.get("maximum", self._mac_max))
                    logger.debug(
                        DEBUG_COMMON,
                        "mac_aver:%f, mac_max:%f" % (self.mac_aver, self._mac_max),
                    )
                else:
                    logger.debug(DEBUG_COMMON, "%%policy:get_mac_status_bcmcmd failed")
            else:
                logger.debug(DEBUG_COMMON, "%%policy:get_mac_status_bcmcmd SDK not OK")
            return 0
        except AttributeError as e:
            logger.error(str(e))
        return -1

    def get_mac_status_sysfs(self, conf):
        try:
            sta, ret = get_mac_temp_sysfs(conf)
            if sta == True:
                self._mac_aver = float(ret) / 1000
                self._mac_max = float(ret) / 1000
                logger.debug(
                    DEBUG_COMMON,
                    "mac_aver:%f, mac_max:%f" % (self.mac_aver, self._mac_max),
                )
            elif conf.get("try_bcmcmd", 0) == 1:
                logger.debug(
                    DEBUG_COMMON, "get sysfs mac temp failed.try to use bcmcmd",
                )
                self.get_mac_status_bcmcmd()
            else:
                logger.debug(DEBUG_COMMON, "%%policy:get_mac_status_sysfs failed")
            return 0
        except AttributeError as e:
            logger.error(str(e))
        return -1

    def get_mac_status(self):
        try:
            mactempconf = MONITOR_DEV_STATUS.get("mac_temp", None)
            if mactempconf is not None:
                self.get_mac_status_sysfs(mactempconf)
            else:
                self.get_mac_status_bcmcmd()
            return 0
        except AttributeError as e:
            logger.error(str(e))
        return -1

    def set_slot_attr(self, val):
        u"""set each slot present status attribute"""
        for item in val:
            slotid = item.get("id")
            slotattr = slotid + "status"
            slotstatus = item.get("status")
            setattr(FanControl, slotattr, slotstatus)
            logger.debug(
                DEBUG_COMMON, "slotattr:%s,slotstatus:%s" % (slotattr, slotstatus),
            )

    def get_slot_status(self):
        try:
            curSlotStatus = []
            ret = self.checkslot(curSlotStatus)
            if ret == True:
                self.set_slot_attr(curSlotStatus)
                logger.debug(DEBUG_COMMON, "%%policy:get_slot_status success")
        except AttributeError as e:
            logger.error(str(e))
        return 0

    def fanctrol(self):  # fan speed-adjustment
        try:
            if self.preIntemp <= -1000:
                self.preIntemp = self.intemp
            logger.debug(
                DEBUG_FANCONTROL,
                "%%policy:previous temperature[%.2f] , current temperature[%.2f]"
                % (self.preIntemp, self.intemp),
            )
            if self.intemp < MONITOR_CONST.TEMP_MIN:
                logger.debug(
                    DEBUG_FANCONTROL,
                    "%%policy:inlet  %.2f  minimum temperature: %.2f"
                    % (self.intemp, MONITOR_CONST.TEMP_MIN),
                )
                self.set_fan_speed(MONITOR_CONST.DEFAULT_SPEED)  # default level
            elif self.intemp >= MONITOR_CONST.TEMP_MIN and self.intemp > self.preIntemp:
                logger.debug(DEBUG_FANCONTROL, "%%policy:increase temperature")
                self.policy_speed(self.intemp)
            elif (
                self.intemp >= MONITOR_CONST.TEMP_MIN
                and (self.preIntemp - self.intemp) > MONITOR_CONST.MONITOR_FALL_TEMP
            ):
                logger.debug(
                    DEBUG_FANCONTROL,
                    "%%policy:temperature reduce over %d degree"
                    % MONITOR_CONST.MONITOR_FALL_TEMP,
                )
                self.policy_speed(self.intemp)
            else:
                speed = (
                    self.get_curr_speed()
                )  # set according to current speed, prevent fan watch-dog
                if speed is not None:
                    self.set_fan_speed(speed)
                logger.debug(DEBUG_FANCONTROL, "%%policy:change nothing")
        except Exception as e:
            logger.error("%%policy: fancontrol error")

    def start_fan_ctrl(self):
        """
        start speed-adjustment
        """
        self.check_crit()
        if (
            self.critnum == 0
            and self.check_warn() == False
            and self.detect_fan_status() == True
        ):
            self.fanctrol()
            self.check_dev_err()
        logger.debug(
            DEBUG_FANCONTROL,
            "%%policy: speed after speed-adjustment is %0x" % (self.get_curr_speed()),
        )

    def policy_speed(self, temp):  # fan speed-adjustment algorithm
        logger.debug(DEBUG_FANCONTROL, "%%policy:fan speed-adjustment algorithm")
        sped_level = MONITOR_CONST.DEFAULT_SPEED + MONITOR_CONST.K * (
            temp - MONITOR_CONST.TEMP_MIN
        )
        self.set_fan_speed(sped_level)
        self.preIntemp = self.intemp

    def board_moni_msg(self, ledcontrol=False):
        ret_t = 0
        try:
            ret_t += (
                self.get_fan_status()
            )  # get fan status, get number of fan which status is OK
            ret_t += (
                self.get_temp_status()
            )  # get inlet, outlet, hot-point temperature, CPU temperature
            ret_t += self.get_mac_status()  # get MAC highest and average temperature
            if ledcontrol == True:
                ret_t += self.get_slot_status()  # get slot present status
                ret_t += self.get_psu_status()  # get psu status
            if ret_t == 0:
                return True
        except Exception as e:
            logger.error(str(e))
        return False

    # device error algorithm    Tmac-Tin >= 50, or Tmac-Tin <= -50
    def check_dev_err(self):
        try:
            if (self.mac_aver - self.intemp) >= MONITOR_CONST.MAC_UP_TEMP or (
                self.mac_aver - self.intemp
            ) <= MONITOR_CONST.MAC_LOWER_TEMP:
                logger.debug(
                    DEBUG_FANCONTROL, "%%DEV_MONITOR-TEMP: MAC temp get failed.",
                )
                value = self.get_curr_speed()
                if MONITOR_CONST.MAC_ERROR_SPEED >= value:
                    self.set_fan_speed(MONITOR_CONST.MAC_ERROR_SPEED)
                else:
                    self.set_fan_max_speed()
            else:
                pass
        except Exception as e:
            logger.error("%%policy:check_dev_err failed")
            logger.error(str(e))

    def check_temp_warn(self):
        u"""check whether temperature above the normal alarm value"""
        try:
            if (
                self._mac_aver >= MONITOR_CONST.MAC_WARNING_THRESHOLD
                or self._outtemp >= MONITOR_CONST.OUTTEMP_WARNING_THRESHOLD
                or self._boardtemp >= MONITOR_CONST.BOARDTEMP_WARNING_THRESHOLD
                or self._cputemp >= MONITOR_CONST.CPUTEMP_WARNING_THRESHOLD
                or self._intemp >= MONITOR_CONST.INTEMP_WARNING_THRESHOLD
            ):
                logger.debug(
                    DEBUG_COMMON,
                    "check whether temperature above the normal alarm value",
                )
                return True
        except Exception as e:
            logger.error("%%policy: check_temp_warn failed")
            logger.error(str(e))
        return False

    def check_temp_crit(self):
        u"""check whether temperature above the critical alarm value"""
        try:
            if self._mac_aver >= MONITOR_CONST.MAC_CRITICAL_THRESHOLD or (
                self._outtemp >= MONITOR_CONST.OUTTEMP_CRITICAL_THRESHOLD
                and self._boardtemp >= MONITOR_CONST.BOARDTEMP_CRITICAL_THRESHOLD
                and self._cputemp >= MONITOR_CONST.CPUTEMP_CRITICAL_THRESHOLD
                and self._intemp >= MONITOR_CONST.INTEMP_CRITICAL_THRESHOLD
            ):
                logger.debug(
                    DEBUG_COMMON, "temperature above the critical alarm value",
                )
                return True
        except Exception as e:
            logger.error("%%policy: check_temp_crit failed")
            logger.error(str(e))
        return False

    def check_fan_status(self):
        u"""check fan status"""
        for item in MONITOR_FAN_STATUS:
            maxoknum = item.get("maxOkNum")
            minoknum = item.get("minOkNum")
            status = item.get("status")
            if self.normal_fans >= minoknum and self.normal_fans <= maxoknum:
                logger.debug(
                    DEBUG_COMMON,
                    "check_fan_status:normal_fans:%d,status:%s"
                    % (self.normal_fans, status),
                )
                return status
        logger.debug(
            DEBUG_COMMON, "check_fan_status Error:normal_fans:%d" % (self.normal_fans),
        )
        return None

    def check_psu_status(self):
        u"""check psu status"""
        for item in MONITOR_PSU_STATUS:
            maxoknum = item.get("maxOkNum")
            minoknum = item.get("minOkNum")
            status = item.get("status")
            if self.normal_psus >= minoknum and self.normal_psus <= maxoknum:
                logger.debug(
                    DEBUG_COMMON,
                    "check_psu_status:normal_psus:%d,status:%s"
                    % (self.normal_psus, status),
                )
                return status
        logger.debug(
            DEBUG_COMMON, "check_psu_status Error:normal_psus:%d" % (self.normal_psus),
        )
        return None

    def deal_sys_led_status(self):
        u"""set up SYSLED according to temperature, fan and psu status"""
        try:
            fanstatus = self.check_fan_status()
            psustatus = self.check_psu_status()
            if (
                self.check_temp_crit() == True
                or fanstatus == "red"
                or psustatus == "red"
            ):
                status = "red"
            elif (
                self.check_temp_warn() == True
                or fanstatus == "yellow"
                or psustatus == "yellow"
            ):
                status = "yellow"
            else:
                status = "green"
            self.set_sys_leds(status)
            logger.debug(
                DEBUG_LEDCONTROL,
                "%%ledcontrol:deal_sys_led_status success, status:%s," % status,
            )
        except Exception as e:
            logger.error(str(e))

    def deal_sys_fan_led_status(self):
        u"""light panel fan led according to status"""
        try:
            status = self.check_fan_status()
            if status is not None:
                self.set_sys_fan_leds(status)
                logger.debug(
                    DEBUG_LEDCONTROL,
                    "%%ledcontrol:deal_sys_fan_led_status success, status:%s," % status,
                )
        except Exception as e:
            logger.error("%%ledcontrol:deal_sys_led_status error")
            logger.error(str(e))

    def deal_psu_led_status(self):
        u"""set up PSU-LED according to psu status"""
        try:
            status = self.check_psu_status()
            if status is not None:
                self.set_sys_psu_leds(status)
            logger.debug(
                DEBUG_LEDCONTROL,
                "%%ledcontrol:deal_psu_led_status success, status:%s," % status,
            )
        except Exception as e:
            logger.error("%%ledcontrol:deal_psu_led_status error")
            logger.error(str(e))

    def deal_fan_led_status(self):
        u"""light fan led according to fan status"""
        for item in MONITOR_FANS_LED:
            try:
                index = MONITOR_FANS_LED.index(item) + 1
                fanattr = "fan%dstatus" % index
                val_t = getattr(FanControl, fanattr, None)
                if val_t == "NOT OK":
                    rgi2cset(item["bus"], item["devno"], item["addr"], item["red"])
                elif val_t == "OK":
                    rgi2cset(item["bus"], item["devno"], item["addr"], item["green"])
                else:
                    pass
                logger.debug(
                    DEBUG_LEDCONTROL,
                    "%%ledcontrol:dealLocFanLed success.fanattr:%s, status:%s"
                    % (fanattr, val_t),
                )
            except Exception as e:
                logger.error("%%ledcontrol:deal_fan_led_status error")
                logger.error(str(e))

    def dealSlotLedStatus(self):
        u"""light slot status led according to slot present status"""
        slotLedList = DEV_LEDS.get("SLOTLED", [])
        for item in slotLedList:
            try:
                index = slotLedList.index(item) + 1
                slotattr = "slot%dstatus" % index
                val_t = getattr(FanControl, slotattr, None)
                if val_t == "PRESENT":
                    rgi2cset(item["bus"], item["devno"], item["addr"], item["green"])
                logger.debug(
                    DEBUG_LEDCONTROL,
                    "%%ledcontrol:dealSlotLedStatus success.slotattr:%s, status:%s"
                    % (slotattr, val_t),
                )
            except Exception as e:
                logger.error("%%ledcontrol:dealSlotLedStatus error")
                logger.error(str(e))

    def setled(self, item, color):
        if item.get("type", "i2c") == "sysfs":
            rgsysset(item["cmdstr"], item.get(color))
        else:
            mask = item.get("mask", 0xFF)
            ind, val = rgi2cget(item["bus"], item["devno"], item["addr"])
            if ind == True:
                setval = (int(val, 16) & ~mask) | item.get(color)
                rgi2cset(item["bus"], item["devno"], item["addr"], setval)
            else:
                logger.error("led %s" % "i2c read failed")

    def set_sys_leds(self, color):
        for item in MONITOR_SYS_LED:
            self.setled(item, color)

    def set_sys_fan_leds(self, color):
        for item in MONITOR_SYS_FAN_LED:
            self.setled(item, color)

    def set_sys_psu_leds(self, color):
        for item in MONITOR_SYS_PSU_LED:
            self.setled(item, color)

    def check_warn(self):
        try:
            if self.check_temp_warn() == True:
                logger.debug(DEBUG_FANCONTROL, "anti-shake start")
                time.sleep(MONITOR_CONST.SHAKE_TIME)
                logger.debug(DEBUG_FANCONTROL, "anti-shake end")
                self.board_moni_msg()  # re-read
                if self.check_temp_warn() == True:
                    logger.warn("%%DEV_MONITOR-TEMP:The temperature of device is over warning value.")
                    self.set_fan_max_speed()  # fan full speed
                    return True
        except Exception as e:
            logger.error("%%policy: check_warn failed")
            logger.error(str(e))
        return False

    def check_crit(self):
        try:
            if self.check_temp_crit() == True:
                logger.debug(DEBUG_FANCONTROL, "anti-shake start")
                time.sleep(MONITOR_CONST.SHAKE_TIME)
                logger.debug(DEBUG_FANCONTROL, "anti-shake end")
                self.board_moni_msg()  # re-read
                if self.check_temp_crit() == True:
                    logger.crit(
                        "%%DEV_MONITOR-TEMP:The temperature of device is over critical value.",
                    )
                    self.set_fan_max_speed()  # fan full speed
                    self.critnum += 1  # anti-shake
                    if self.critnum >= MONITOR_CONST.CRITICAL_NUM:
                        os.system("reboot")
                    logger.debug(DEBUG_FANCONTROL, "crit times:%d" % self.critnum)
                else:
                    self.critnum = 0
            else:
                self.critnum = 0
        except Exception as e:
            logger.error("%%policy: check_crit failed")
            logger.error(str(e))


def callback():
    pass


def do_fan_ctrl(fanctrl):
    ret = fanctrl.board_moni_msg()
    if ret == True:
        logger.debug(DEBUG_FANCONTROL, "%%policy:start_fan_ctrl")
        fanctrl.start_fan_ctrl()
    else:
        fanctrl.set_fan_max_speed()
        logger.debug(DEBUG_FANCONTROL, "%%policy:board_moni_msg error")


def do_led_ctrl(fanctrl):
    fanctrl.board_moni_msg(ledcontrol=True)  # get status
    fanctrl.deal_sys_led_status()  # light system led
    fanctrl.deal_sys_fan_led_status()  # light panel fan led
    fanctrl.deal_fan_led_status()  # light fan led
    fanctrl.deal_psu_led_status()  # light psu led
    fanctrl.dealSlotLedStatus()  # light slot status led
    logger.debug(DEBUG_LEDCONTROL, "%%ledcontrol:do_led_ctrl success")


def run(interval, fanctrl):
    loop = 0
    # waitForDocker()
    while True:
        try:
            if loop % MONITOR_CONST.MONITOR_INTERVAL == 0:  # fan speed-adjustment
                logger.debug(DEBUG_FANCONTROL, "%%policy:fanctrl")
                do_fan_ctrl(fanctrl)
            else:
                logger.debug(
                    DEBUG_LEDCONTROL, "%%ledcontrol:start ledctrol"
                )  # LED control
                do_led_ctrl(fanctrl)
            time.sleep(interval)
            loop += interval
        except Exception as e:
            traceback.print_exc()
            logger.error(str(e))


@click.group(cls=AliasedGroup, context_settings=CONTEXT_SETTINGS)
def main():
    """device operator"""
    pass


@main.command()
def start():
    """start fan control"""
    logger.info("FAN CTRL START")
    fanctrl = FanControl()
    interval = MONITOR_CONST.MONITOR_INTERVAL / 30
    run(interval, fanctrl)


@main.command()
def stop():
    """stop fan control """
    logger.info("FAN CTRL STOP")


##device_i2c operation
if __name__ == "__main__":
    main()

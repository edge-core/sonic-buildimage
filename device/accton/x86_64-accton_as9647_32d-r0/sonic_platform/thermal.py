#############################################################################
# Edgecore
#
# Thermal contains an implementation of SONiC Platform Base API and
# provides the thermal device status which are available in the platform
#
#############################################################################

import os
import glob
import time
import threading

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from sonic_py_common.logger import Logger
    from .thermal_device_data import DEVICE_DATA
    from .helper import APIHelper
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

logger = Logger()
# To enable messages of log_debug verbosity, uncomment the below line
# logger.set_min_log_priority_debug()

class Thermal(ThermalBase):
    """Platform-specific Thermal class"""
    NUMBER_OF_THERMALS = 12
    CPU_TEMP_SENSORS_OFFSET = 11
    ASIC_TEMP_SENSORS_OFFSET = 8
    SYSFS_PATH = "/sys/bus/i2c/devices"
    _db_thermals = None
    _db_lock = threading.Lock()

    def __init__(self, thermal_index=0):
        self._api_helper = APIHelper()

        self.index = thermal_index
        # Add thermal name
        self.THERMAL_NAME_LIST = []
        self.THERMAL_NAME_LIST.append("PCB VDD_Core")
        self.THERMAL_NAME_LIST.append("PCB FP Hotspot")
        self.THERMAL_NAME_LIST.append("PCB Top Front")
        self.THERMAL_NAME_LIST.append("PCB Bottom Front")
        self.THERMAL_NAME_LIST.append("PCB Bottom Rear")
        self.THERMAL_NAME_LIST.append("PCB OCXO")
        self.THERMAL_NAME_LIST.append("PCB ASIC")
        self.THERMAL_NAME_LIST.append("PCB Top Rear")
        self.THERMAL_NAME_LIST.append("ASIC Temp 1")
        self.THERMAL_NAME_LIST.append("ASIC Temp 2")
        self.THERMAL_NAME_LIST.append("ASIC Temp 3")
        self.THERMAL_NAME_LIST.append("CPU Temp")

        if self.index < Thermal.ASIC_TEMP_SENSORS_OFFSET:
            i2c_path = {
                0: "11-0048/hwmon/hwmon*/",
                1: "11-0049/hwmon/hwmon*/",
                2: "11-004a/hwmon/hwmon*/",
                3: "11-004b/hwmon/hwmon*/",
                4: "11-004c/hwmon/hwmon*/",
                5: "11-004d/hwmon/hwmon*/",
                6: "11-004e/hwmon/hwmon*/",
                7: "11-004f/hwmon/hwmon*/",
            }.get(self.index, None)

            self.hwmon_path = "{}/{}".format(self.SYSFS_PATH, i2c_path)

        self.ss_index = 1

        self.minimum_thermal = None
        self.maximum_thermal = None

    def __read_txt_file_with_glob(self, file_path):
        data = None
        for filename in glob.glob(file_path):
            try:
                with open(filename, 'r') as fd:
                    data = fd.readline().rstrip()
                    break
            except IOError as e:
                pass

        return data

    def __get_round_temp(self, temp, divisor):
        round_temp = None
        try:
            round_temp = round(float(temp) / divisor, 1)
        except (ValueError, TypeError) as e:
            logger.log_error("Failed to read temperature sensor {}: {}".format(self.get_name(), e))
        return round_temp

    def __get_pcb_temp(self):
        temp_file = "temp{}_input".format(self.ss_index)
        temp_file_path = os.path.join(self.hwmon_path, temp_file)
        temp = self.__read_txt_file_with_glob(temp_file_path)
        return self.__get_round_temp(temp, 1000)

    def __get_asic_temp(self):
        temp = None

        if Thermal._db_thermals is None:
            with Thermal._db_lock:
               if Thermal._db_thermals is None:
                    try:
                        from swsscommon.swsscommon import SonicV2Connector
                        db = SonicV2Connector()
                        db.connect(db.STATE_DB)
                        Thermal._db_thermals = db
                    except Exception as e:
                        logger.log_error("Failed to connect to STATE_DB: {}".format(e))

        if Thermal._db_thermals is not None:
            try:
                tbl = Thermal._db_thermals.get_all(Thermal._db_thermals.STATE_DB, 'ASIC_TEMPERATURE_INFO')
                temp = tbl.get("temperature_{}".format(self.index - Thermal.ASIC_TEMP_SENSORS_OFFSET), None)
            except Exception as e:
                logger.log_error("Failed to get ASIC temperature from DB: {}".format(e))

        return self.__get_round_temp(temp, 1)

    def __get_cpu_temp(self):
        temp_file_path = "/sys/class/hwmon/hwmon2/temp1_input"
        temp = self._api_helper.read_txt_file(temp_file_path)
        return self.__get_round_temp(temp, 1000)

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal
        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        temp = None
        try:
            if self.index < Thermal.ASIC_TEMP_SENSORS_OFFSET:
                temp = self.__get_pcb_temp()
            elif self.index < Thermal.CPU_TEMP_SENSORS_OFFSET:
                temp = self.__get_asic_temp()
            elif self.index < Thermal.NUMBER_OF_THERMALS:
                temp = self.__get_cpu_temp()
        except Exception as e:
            logger.log_error("Failed to get temperature for thermal index {}: {}".format(self.index, e))

        return temp

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        threshold = None
        if self.index >= 0 and self.index < Thermal.NUMBER_OF_THERMALS:
            temp_list = DEVICE_DATA['thresholds'][self.index]
            thresh_list = temp_list[len(temp_list) - 2].split(':')
            threshold = float(thresh_list[1])
        return threshold

    def get_low_threshold(self):
        """
        Retrieves the high threshold temperature of thermal
        Returns:
            A float number, the low threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 0.0
        """
        return 0.1

    def get_low_critical_threshold(self):
        """
        Retrieves the low critical threshold temperature of thermal
        Returns:
            A float number, the low critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        return 0.1

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        threshold = None
        if self.index >= 0 and self.index < Thermal.NUMBER_OF_THERMALS:
            temp_list = DEVICE_DATA['thresholds'][self.index]
            thresh_list = temp_list[len(temp_list) - 1].split(':')
            threshold = float(thresh_list[1])
        return threshold

    def get_name(self):
        """
        Retrieves the name of the thermal device
            Returns:
            string: The name of the thermal device
        """
        return self.THERMAL_NAME_LIST[self.index]

    def get_model(self):
        """
        Retrieves the model of the thermal device
            Returns:
            string: The model of the thermal device
        """
        model = None
        if self.index < Thermal.ASIC_TEMP_SENSORS_OFFSET:
            model = "LM75BD"
        elif self.index < Thermal.CPU_TEMP_SENSORS_OFFSET:
            model = "Xsight ASIC"
        elif self.index < Thermal.NUMBER_OF_THERMALS:
            model = "Host CPU"
        return model

    def get_serial(self):
        """
        Retrieves the model of the thermal device
            Returns:
            string: The model of the thermal device
        """
        return "N/A"

    def is_replaceable(self):
        """
        Retrieves is the thermal device replaceable
            Returns:
            boolean: false
        """
        return False

    def get_presence(self):
        """
        Retrieves the presence of the Thermal
        Returns:
            bool: True if Thermal is present, False if not
        """
        presence = False
        if self.index < Thermal.ASIC_TEMP_SENSORS_OFFSET:
            temp = self.__get_pcb_temp()
            if temp is not None:
                presence = True
        else:
            presence = True
        return presence

    def get_status(self):
        """
        Retrieves the operational status of the device
        Returns:
            A boolean value, True if device is operating properly, False if not
        """
        return self.get_presence()

    def get_minimum_recorded(self):
        """
        Retrieves the minimum recorded temperature of thermal
        Returns:
            A float number, the minimum recorded temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        tmp = self.get_temperature()
        if isinstance(tmp, float):
            if self.minimum_thermal is None or tmp < self.minimum_thermal:
                self.minimum_thermal = tmp
        return self.minimum_thermal

    def get_maximum_recorded(self):
        """
        Retrieves the maximum recorded temperature of thermal
        Returns:
            A float number, the maximum recorded temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        tmp = self.get_temperature()
        if isinstance(tmp, float):
            if self.maximum_thermal is None or tmp > self.maximum_thermal:
                self.maximum_thermal = tmp
        return self.maximum_thermal

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device.
        Returns:
            integer: The 1-based relative physical position in parent device
        """
        return (self.index + 1)


class SfpThermal(ThermalBase):
    THRESH_DELAY = 1 # 1 second

    def __init__(self, sfp):
        ThermalBase.__init__(self)
        self._sfp = sfp
        self._minimum = None
        self._maximum = None
        self._cachedThreshInfo = None
        self._cachedThreshInfoTime = 0

    def get_name(self):
        return "{} {}".format(self._sfp.sfp_type, self._sfp.get_id() + 1)

    def get_presence(self):
        return self._sfp.get_presence()

    def get_model(self):
        return "N/A"

    def get_serial(self):
        return "N/A"

    def get_status(self):
        return self.get_temperature() is not None

    def get_position_in_parent(self):
        return 1

    def is_replaceable(self):
        return False

    def get_temperature(self):
        value = self._sfp.get_temperature()
        if not isinstance(value, float):
            return None
        if self._minimum is None or self._minimum > value:
            self._minimum = value
        if self._maximum is None or self._maximum < value:
            self._maximum = value
        return value

    def _get_threshold_info(self):
        currTime = time.time()
        if currTime - self._cachedThreshInfoTime > self.THRESH_DELAY:
            self._cachedThreshInfoTime = currTime
            self._cachedThreshInfo = self._sfp.get_transceiver_threshold_info()
        return self._cachedThreshInfo

    def get_low_threshold(self):
        threshInfo = self._get_threshold_info()
        if threshInfo:
            lowThreshold = threshInfo.get("templowwarning")
        if not threshInfo or lowThreshold == "N/A":
            return None
        return lowThreshold

    def get_low_critical_threshold(self):
        threshInfo = self._get_threshold_info()
        if threshInfo:
            lowCritThreshold = threshInfo.get("templowalarm")
        if not threshInfo or lowCritThreshold == "N/A":
            return None
        return lowCritThreshold

    def get_high_threshold(self):
        threshInfo = self._get_threshold_info()
        if threshInfo:
            highThreshold = threshInfo.get("temphighwarning")
        if not threshInfo or highThreshold == "N/A":
            return None
        return highThreshold

    def get_high_critical_threshold(self):
        threshInfo = self._get_threshold_info()
        if threshInfo:
            highCritThreshold = threshInfo.get("temphighalarm")
        if not threshInfo or highCritThreshold == "N/A":
            return None
        return highCritThreshold

    def get_minimum_recorded(self):
        self.get_temperature()
        return self._minimum

    def get_maximum_recorded(self):
        self.get_temperature()
        return self._maximum

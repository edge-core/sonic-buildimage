#!/usr/bin/env python

#############################################################################
# Mellanox
#
# Module contains an implementation of SONiC Platform Base API and
# provides the thermals data which are available in the platform
#
#############################################################################

try:
    from sonic_platform_base.thermal_base import ThermalBase
    from sonic_py_common.logger import Logger
    from os import listdir
    from os.path import isfile, join
    import io
    import os.path
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

THERMAL_DEV_CATEGORY_CPU_CORE = "cpu_core"
THERMAL_DEV_CATEGORY_CPU_PACK = "cpu_pack"
THERMAL_DEV_CATEGORY_MODULE = "module"
THERMAL_DEV_CATEGORY_PSU = "psu"
THERMAL_DEV_CATEGORY_GEARBOX = "gearbox"
THERMAL_DEV_CATEGORY_AMBIENT = "ambient"

THERMAL_DEV_ASIC_AMBIENT = "asic_amb"
THERMAL_DEV_FAN_AMBIENT = "fan_amb"
THERMAL_DEV_PORT_AMBIENT = "port_amb"
THERMAL_DEV_COMEX_AMBIENT = "comex_amb"
THERMAL_DEV_BOARD_AMBIENT = "board_amb"

THERMAL_API_GET_TEMPERATURE = "get_temperature"
THERMAL_API_GET_HIGH_THRESHOLD = "get_high_threshold"
THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD = "get_high_critical_threshold"

THERMAL_API_INVALID_HIGH_THRESHOLD = 0.0

HW_MGMT_THERMAL_ROOT = "/var/run/hw-management/thermal/"

THERMAL_ZONE_ASIC_PATH = "/var/run/hw-management/thermal/mlxsw/"
THERMAL_ZONE_MODULE_PATH = "/var/run/hw-management/thermal/mlxsw-module{}/"
THERMAL_ZONE_GEARBOX_PATH = "/var/run/hw-management/thermal/mlxsw-gearbox{}/"
THERMAL_ZONE_MODE = "thermal_zone_mode"
THERMAL_ZONE_POLICY = "thermal_zone_policy"
THERMAL_ZONE_TEMPERATURE = "thermal_zone_temp"
THERMAL_ZONE_NORMAL_TEMPERATURE = "temp_trip_norm"

MODULE_TEMPERATURE_FAULT_PATH = "/var/run/hw-management/thermal/module{}_temp_fault"

thermal_api_handler_asic = {
    THERMAL_API_GET_TEMPERATURE: 'asic',
    THERMAL_API_GET_HIGH_THRESHOLD: 'mlxsw/temp_trip_hot',
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD: 'mlxsw/temp_trip_crit'
}

thermal_api_handler_cpu_core = {
    THERMAL_API_GET_TEMPERATURE:"cpu_core{}",
    THERMAL_API_GET_HIGH_THRESHOLD:"cpu_core{}_max",
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD:"cpu_core{}_crit"
}
thermal_api_handler_cpu_pack = {
    THERMAL_API_GET_TEMPERATURE:"cpu_pack",
    THERMAL_API_GET_HIGH_THRESHOLD:"cpu_pack_max",
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD:"cpu_pack_crit"
}
thermal_api_handler_module = {
    THERMAL_API_GET_TEMPERATURE:"module{}_temp_input",
    THERMAL_API_GET_HIGH_THRESHOLD:"module{}_temp_crit",
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD:"module{}_temp_emergency"
}
thermal_api_handler_psu = {
    THERMAL_API_GET_TEMPERATURE:"psu{}_temp",
    THERMAL_API_GET_HIGH_THRESHOLD:"psu{}_temp_max",
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD:None
}
thermal_api_handler_gearbox = {
    THERMAL_API_GET_TEMPERATURE:"gearbox{}_temp_input",
    THERMAL_API_GET_HIGH_THRESHOLD:None,
    THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD:None
}
thermal_ambient_apis = {
    THERMAL_DEV_ASIC_AMBIENT : thermal_api_handler_asic,
    THERMAL_DEV_PORT_AMBIENT : "port_amb",
    THERMAL_DEV_FAN_AMBIENT : "fan_amb",
    THERMAL_DEV_COMEX_AMBIENT : "comex_amb",
    THERMAL_DEV_BOARD_AMBIENT : "board_amb"
}
thermal_ambient_name = {
    THERMAL_DEV_ASIC_AMBIENT : 'ASIC',
    THERMAL_DEV_PORT_AMBIENT : "Ambient Port Side Temp",
    THERMAL_DEV_FAN_AMBIENT : "Ambient Fan Side Temp",
    THERMAL_DEV_COMEX_AMBIENT : "Ambient COMEX Temp",
    THERMAL_DEV_BOARD_AMBIENT : "Ambient Board Temp"
}
thermal_api_handlers = {
    THERMAL_DEV_CATEGORY_CPU_CORE : thermal_api_handler_cpu_core, 
    THERMAL_DEV_CATEGORY_CPU_PACK : thermal_api_handler_cpu_pack,
    THERMAL_DEV_CATEGORY_MODULE : thermal_api_handler_module,
    THERMAL_DEV_CATEGORY_PSU : thermal_api_handler_psu,
    THERMAL_DEV_CATEGORY_GEARBOX : thermal_api_handler_gearbox
}
thermal_name = {
    THERMAL_DEV_CATEGORY_CPU_CORE : "CPU Core {} Temp", 
    THERMAL_DEV_CATEGORY_CPU_PACK : "CPU Pack Temp",
    THERMAL_DEV_CATEGORY_MODULE : "xSFP module {} Temp",
    THERMAL_DEV_CATEGORY_PSU : "PSU-{} Temp",
    THERMAL_DEV_CATEGORY_GEARBOX : "Gearbox {} Temp"
}

thermal_device_categories_all = [
    THERMAL_DEV_CATEGORY_CPU_CORE,
    THERMAL_DEV_CATEGORY_CPU_PACK,
    THERMAL_DEV_CATEGORY_MODULE,
    THERMAL_DEV_CATEGORY_PSU,
    THERMAL_DEV_CATEGORY_AMBIENT,
    THERMAL_DEV_CATEGORY_GEARBOX
]

thermal_device_categories_singleton = [
    THERMAL_DEV_CATEGORY_CPU_PACK,
    THERMAL_DEV_CATEGORY_AMBIENT
]
thermal_api_names = [
    THERMAL_API_GET_TEMPERATURE,
    THERMAL_API_GET_HIGH_THRESHOLD
]

platform_dict_thermal = {'x86_64-mlnx_msn2700-r0': 0, 'x86_64-mlnx_lssn2700-r0':0, 'x86_64-mlnx_msn2740-r0': 3, 'x86_64-mlnx_msn2100-r0': 1, 'x86_64-mlnx_msn2410-r0': 2, 'x86_64-mlnx_msn2010-r0': 4, 'x86_64-mlnx_msn3420-r0':9, 'x86_64-mlnx_msn3700-r0': 5, 'x86_64-mlnx_msn3700c-r0': 6, 'x86_64-mlnx_msn3800-r0': 7, 'x86_64-mlnx_msn4600c-r0':9, 'x86_64-mlnx_msn4700-r0': 8}
thermal_profile_list = [
    # 2700
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 2100
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 16),
        THERMAL_DEV_CATEGORY_PSU:(0, 0),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2410
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 56),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2740
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 2010
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 22),
        THERMAL_DEV_CATEGORY_PSU:(0, 0),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,0),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT,
            ]
        )
    },
    # 3700
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 3700c
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 3800
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 64),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(1,32),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 4700
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 32),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 3420
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 2),
        THERMAL_DEV_CATEGORY_MODULE:(1, 60),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    },
    # 4600C
    {
        THERMAL_DEV_CATEGORY_CPU_CORE:(0, 4),
        THERMAL_DEV_CATEGORY_MODULE:(1, 64),
        THERMAL_DEV_CATEGORY_PSU:(1, 2),
        THERMAL_DEV_CATEGORY_CPU_PACK:(0,1),
        THERMAL_DEV_CATEGORY_GEARBOX:(0,0),
        THERMAL_DEV_CATEGORY_AMBIENT:(0,
            [
                THERMAL_DEV_ASIC_AMBIENT,
                THERMAL_DEV_COMEX_AMBIENT,
                THERMAL_DEV_PORT_AMBIENT,
                THERMAL_DEV_FAN_AMBIENT
            ]
        )
    }
]


def initialize_thermals(platform, thermal_list, psu_list):
    # create thermal objects for all categories of sensors
    tp_index = platform_dict_thermal[platform]
    thermal_profile = thermal_profile_list[tp_index]
    Thermal.thermal_profile = thermal_profile
    for category in thermal_device_categories_all:
        if category == THERMAL_DEV_CATEGORY_AMBIENT:
            count, ambient_list = thermal_profile[category]
            for ambient in ambient_list:
                thermal = Thermal(category, ambient, True)
                thermal_list.append(thermal)
        else:
            start, count = 0, 0
            if category in thermal_profile:
                start, count = thermal_profile[category]
                if count == 0:
                    continue
            if count == 1:
                thermal = Thermal(category, 0, False)
                thermal_list.append(thermal)
            else:
                if category == THERMAL_DEV_CATEGORY_PSU:
                    for index in range(count):
                        thermal = Thermal(category, start + index, True, psu_list[index].get_power_available_status)
                        thermal_list.append(thermal)
                else:
                    for index in range(count):
                        thermal = Thermal(category, start + index, True)
                        thermal_list.append(thermal)



class Thermal(ThermalBase):
    thermal_profile = None
    thermal_algorithm_status = False

    def __init__(self, category, index, has_index, dependency = None):
        """
        index should be a string for category ambient and int for other categories
        """
        if category == THERMAL_DEV_CATEGORY_AMBIENT:
            self.name = thermal_ambient_name[index]
            self.index = index
        elif has_index:
            self.name = thermal_name[category].format(index)
            self.index = index
        else:
            self.name = thermal_name[category]
            self.index = 0

        self.category = category
        self.temperature = self._get_file_from_api(THERMAL_API_GET_TEMPERATURE)
        self.high_threshold = self._get_file_from_api(THERMAL_API_GET_HIGH_THRESHOLD)
        self.high_critical_threshold = self._get_file_from_api(THERMAL_API_GET_HIGH_CRITICAL_THRESHOLD)
        self.dependency = dependency


    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return self.name


    @classmethod
    def _read_generic_file(cls, filename, len):
        """
        Read a generic file, returns the contents of the file
        """
        result = None
        try:
            with open(filename, 'r') as fileobj:
                result = fileobj.read().strip()
        except Exception as e:
            logger.log_info("Fail to read file {} due to {}".format(filename, repr(e)))
        return result


    def _get_file_from_api(self, api_name):
        if self.category == THERMAL_DEV_CATEGORY_AMBIENT:
            handler = thermal_ambient_apis[self.index]
            if isinstance(handler, str):
                if api_name == THERMAL_API_GET_TEMPERATURE:
                    filename = thermal_ambient_apis[self.index]
                else:
                    return None
            elif isinstance(handler, dict):
                filename = handler[api_name]
            else:
                return None
        else:
            handler = thermal_api_handlers[self.category][api_name]
            if self.category in thermal_device_categories_singleton:
                filename = handler
            else:
                if handler:
                    filename = handler.format(self.index)
                else:
                    return None
        return join(HW_MGMT_THERMAL_ROOT, filename)


    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125 
        """
        if self.dependency:
            status, hint = self.dependency()
            if not status:
                logger.log_debug("get_temperature for {} failed due to {}".format(self.name, hint))
                return None
        value_str = self._read_generic_file(self.temperature, 0)
        if value_str is None:
            return None
        value_float = float(value_str)
        if self.category == THERMAL_DEV_CATEGORY_MODULE and value_float == THERMAL_API_INVALID_HIGH_THRESHOLD:
            return None
        return value_float / 1000.0


    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.high_threshold is None:
            return None
        if self.dependency:
            status, hint = self.dependency()
            if not status:
                logger.log_debug("get_high_threshold for {} failed due to {}".format(self.name, hint))
                return None
        value_str = self._read_generic_file(self.high_threshold, 0)
        if value_str is None:
            return None
        value_float = float(value_str)
        if self.category == THERMAL_DEV_CATEGORY_MODULE and value_float == THERMAL_API_INVALID_HIGH_THRESHOLD:
            return None
        return value_float / 1000.0


    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.high_critical_threshold is None:
            return None
        if self.dependency:
            status, hint = self.dependency()
            if not status:
                logger.log_debug("get_high_critical_threshold for {} failed due to {}".format(self.name, hint))
                return None
        value_str = self._read_generic_file(self.high_critical_threshold, 0)
        if value_str is None:
            return None
        value_float = float(value_str)
        if self.category == THERMAL_DEV_CATEGORY_MODULE and value_float == THERMAL_API_INVALID_HIGH_THRESHOLD:
            return None
        return value_float / 1000.0


    @classmethod
    def _write_generic_file(cls, filename, content):
        """
        Generic functions to write content to a specified file path if 
        the content has changed.
        """
        try:
            with open(filename, 'w+') as file_obj:
                origin_content = file_obj.read()
                if origin_content != content:
                    file_obj.write(content)
        except Exception as e:
            logger.log_info("Fail to write file {} due to {}".format(filename, repr(e)))

    @classmethod
    def set_thermal_algorithm_status(cls, status, force=True):
        """
        Enable/disable kernel thermal algorithm.
        When enable kernel thermal algorithm, kernel will adjust fan speed
        according to thermal zones temperature. Please note that kernel will
        only adjust fan speed when temperature across some "edge", e.g temperature
        changes to exceed high threshold.
        When disable kernel thermal algorithm, kernel no longer adjust fan speed.
        We usually disable the algorithm when we want to set a fix speed. E.g, when 
        a fan unit is removed from system, we will set fan speed to 100% and disable 
        the algorithm to avoid it adjust the speed.

        Returns:
            True if thermal algorithm status changed.
        """
        if not cls.thermal_profile:
            raise Exception("Fail to get thermal profile for this switch")

        if not force and cls.thermal_algorithm_status == status:
            return False

        cls.thermal_algorithm_status = status
        content = "enabled" if status else "disabled"
        policy = "step_wise" if status else "user_space"
        cls._write_generic_file(join(THERMAL_ZONE_ASIC_PATH, THERMAL_ZONE_MODE), content)
        cls._write_generic_file(join(THERMAL_ZONE_ASIC_PATH, THERMAL_ZONE_POLICY), policy)

        if THERMAL_DEV_CATEGORY_MODULE in cls.thermal_profile:
            start, count = cls.thermal_profile[THERMAL_DEV_CATEGORY_MODULE]
            if count != 0:
                for index in range(count):
                    cls._write_generic_file(join(THERMAL_ZONE_MODULE_PATH.format(start + index), THERMAL_ZONE_MODE), content)
                    cls._write_generic_file(join(THERMAL_ZONE_MODULE_PATH.format(start + index), THERMAL_ZONE_POLICY), policy)

        if THERMAL_DEV_CATEGORY_GEARBOX in cls.thermal_profile:
            start, count = cls.thermal_profile[THERMAL_DEV_CATEGORY_GEARBOX]
            if count != 0:
                for index in range(count):
                    cls._write_generic_file(join(THERMAL_ZONE_GEARBOX_PATH.format(start + index), THERMAL_ZONE_MODE), content)
                    cls._write_generic_file(join(THERMAL_ZONE_GEARBOX_PATH.format(start + index), THERMAL_ZONE_POLICY), policy)
        return True

    @classmethod
    def check_thermal_zone_temperature(cls):
        """
        Check thermal zone current temperature with normal temperature

        Returns:
            True if all thermal zones current temperature less or equal than normal temperature
        """
        if not cls.thermal_profile:
            raise Exception("Fail to get thermal profile for this switch")

        if not cls._check_thermal_zone_temperature(THERMAL_ZONE_ASIC_PATH):
            return False

        if THERMAL_DEV_CATEGORY_MODULE in cls.thermal_profile:
            start, count = cls.thermal_profile[THERMAL_DEV_CATEGORY_MODULE]
            if count != 0:
                for index in range(count):
                    if not cls._check_thermal_zone_temperature(THERMAL_ZONE_MODULE_PATH.format(start + index)):
                        return False

        if THERMAL_DEV_CATEGORY_GEARBOX in cls.thermal_profile:
            start, count = cls.thermal_profile[THERMAL_DEV_CATEGORY_GEARBOX]
            if count != 0:
                for index in range(count):
                    if not cls._check_thermal_zone_temperature(THERMAL_ZONE_GEARBOX_PATH.format(start + index)):
                        return False

        return True

    @classmethod
    def _check_thermal_zone_temperature(cls, thermal_zone_path):
        normal_temp_path = join(thermal_zone_path, THERMAL_ZONE_NORMAL_TEMPERATURE)
        current_temp_path = join(thermal_zone_path, THERMAL_ZONE_TEMPERATURE)
        normal = None
        current = None
        try:    
            with open(normal_temp_path, 'r') as file_obj:
                normal = float(file_obj.read())

            with open(current_temp_path, 'r') as file_obj:
                current = float(file_obj.read())

            return current <= normal
        except Exception as e:
            logger.log_info("Fail to check thermal zone temperature for file {} due to {}".format(thermal_zone_path, repr(e)))

    @classmethod
    def check_module_temperature_trustable(cls):
        if not cls.thermal_profile:
            raise Exception("Fail to get thermal profile for this switch")

        start, count = cls.thermal_profile[THERMAL_DEV_CATEGORY_MODULE]
        for index in range(count):
            fault_file_path = MODULE_TEMPERATURE_FAULT_PATH.format(index + start)
            fault = cls._read_generic_file(fault_file_path, 0)
            if fault.strip() != '0':
                return 'untrust'
        return 'trust'

    @classmethod
    def get_min_amb_temperature(cls):
        fan_ambient_path = join(HW_MGMT_THERMAL_ROOT, THERMAL_DEV_FAN_AMBIENT)
        port_ambient_path = join(HW_MGMT_THERMAL_ROOT, THERMAL_DEV_PORT_AMBIENT)

        # if there is any exception, let it raise
        fan_ambient_temp = int(cls._read_generic_file(fan_ambient_path, 0))
        port_ambient_temp = int(cls._read_generic_file(port_ambient_path, 0))
        return fan_ambient_temp if fan_ambient_temp < port_ambient_temp else port_ambient_temp

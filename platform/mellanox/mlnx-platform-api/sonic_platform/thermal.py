#
# Copyright (c) 2019-2021 NVIDIA CORPORATION & AFFILIATES.
# Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
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
    import copy
    import os
    import glob

    from .device_data import DeviceDataManager
    from . import utils
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

# Global logger class instance
logger = Logger()

"""
The most important information for creating a Thermal object is 3 sysfs files: temperature file, high threshold file and
high critical threshold file. There is no common naming rule for thermal objects on Nvidia platform. There are two types
of thermal object: single and indexable:
    1. Single. Such as asic, port_amb...
    2. Indexablt. Such as cpu_core0, cpu_core1, psu1_temp, psu2_temp

Thermal objects can be created according to a pre-defined naming rule. The naming rules contains following fields

Field Name                Mandatory   Default   Description
name                      M                     Thermal object name template
temperature               M                     Temperature file name
high_threshold            O           None      High threshold file name
high_critical_threshold   O           None      High critical threshold file name
type                      O           single    Thermal object type
start_index               O           1         Thermal object start index, only used by indexable thermal object
"""
THERMAL_NAMING_RULE = {
    "sfp thermals":
    {
        "name": "xSFP module {} Temp",
        "temperature": "module{}_temp_input",
        "high_threshold": "module{}_temp_crit",
        "high_critical_threshold": "module{}_temp_emergency",
        "type": "indexable"
    },
    "psu thermals":
    {
        "name": "PSU-{} Temp",
        "temperature": "psu{}_temp",
        "high_threshold": "psu{}_temp_max",
        "type": "indexable"
    },
    "chassis thermals": [
        {
            "name": "ASIC",
            "temperature": "asic",
            "high_threshold": "mlxsw/temp_trip_hot",
            "high_critical_threshold": "mlxsw/temp_trip_crit"
        },
        {
            "name": "Ambient Port Side Temp",
            "temperature": "port_amb"
        },
        {
            "name": "Ambient Fan Side Temp",
            "temperature": "fan_amb"
        },
        {
            "name": "Ambient COMEX Temp",
            "temperature": "comex_amb"
        },
        {
            "name": "CPU Pack Temp",
            "temperature": "cpu_pack",
            "high_threshold": "cpu_pack_max",
            "high_critical_threshold": "cpu_pack_crit"
        },
        {
            "name": "CPU Core {} Temp",
            "temperature": "cpu_core{}",
            "high_threshold": "cpu_core{}_max",
            "high_critical_threshold": "cpu_core{}_crit",
            "type": "indexable",
            "start_index": 0
        },
        {
            "name": "Gearbox {} Temp",
            "temperature": "gearbox{}_temp_input",
            "high_threshold": "mlxsw-gearbox{}/temp_trip_hot",
            "high_critical_threshold": "mlxsw-gearbox{}/temp_trip_crit",
            "type": "indexable"
        },
        {
            "name": "Ambient CPU Board Temp",
            "temperature": "cpu_amb",
            "default_present": False
        },
        {
            "name": "Ambient Switch Board Temp",
            "temperature": "swb_amb",
            "default_present": False
        }
    ],
    'linecard thermals': {
        "name": "Gearbox {} Temp",
        "temperature": "gearbox{}_temp_input",
        "high_threshold": "mlxsw-gearbox{}/temp_trip_hot",
        "high_critical_threshold": "mlxsw-gearbox{}/temp_trip_crit",
        "type": "indexable"
    }
}

CHASSIS_THERMAL_SYSFS_FOLDER = '/run/hw-management/thermal'
COOLING_STATE_PATH = "/var/run/hw-management/thermal/cooling_cur_state"
THERMAL_ZONE_ASIC_PATH = '/var/run/hw-management/thermal/mlxsw/'
THERMAL_ZONE_FOLDER_WILDCARD = '/run/hw-management/thermal/mlxsw*'
THERMAL_ZONE_HIGH_THRESHOLD = 'temp_trip_high'
THERMAL_ZONE_HOT_THRESHOLD = 'temp_trip_hot'
THERMAL_ZONE_NORMAL_THRESHOLD = 'temp_trip_norm'
THERMAL_ZONE_MODE_FILE = 'thermal_zone_mode'
THERMAL_ZONE_POLICY_FILE = 'thermal_zone_policy'
THERMAL_ZONE_TEMP_FILE = 'thermal_zone_temp'
THERMAL_ZONE_HYSTERESIS = 5000
MODULE_TEMP_FAULT_WILDCARRD = '/run/hw-management/thermal/module*_temp_fault'
MAX_AMBIENT_TEMP = 120
# Min allowed cooling level when all thermal zones are in normal state
MIN_COOLING_LEVEL_FOR_NORMAL = 2
# Min allowed cooling level when any thermal zone is in high state but no thermal zone is in emergency state
MIN_COOLING_LEVEL_FOR_HIGH = 4
MAX_COOLING_LEVEL = 10


def initialize_chassis_thermals():
    thermal_list = []
    rules = THERMAL_NAMING_RULE['chassis thermals']
    position = 1
    for rule in rules:
        if 'type' in rule and rule['type'] == 'indexable':
            count = 0
            if 'Gearbox' in rule['name']:
                count = DeviceDataManager.get_gearbox_count('/run/hw-management/config')
            elif 'CPU Core' in rule['name']:
                count = DeviceDataManager.get_cpu_thermal_count()
            if count == 0:
                logger.log_debug('Failed to get thermal object count for {}'.format(rule['name']))
                continue

            for index in range(count):
                thermal_list.append(create_indexable_thermal(rule, index, CHASSIS_THERMAL_SYSFS_FOLDER, position))
                position += 1
        else:
            thermal_object = create_single_thermal(rule, CHASSIS_THERMAL_SYSFS_FOLDER, position)
            if thermal_object:
                thermal_list.append(thermal_object)
                position += 1
    return thermal_list


def initialize_psu_thermal(psu_index, presence_cb):
    """Initialize PSU thermal object

    Args:
        psu_index (int): PSU index, 0-based
        presence_cb (function): A callback function to indicate if the thermal is present. When removing a PSU, the related
            thermal sysfs files will be removed from system, presence_cb is used to check such situation and avoid printing
            error logs.

    Returns:
        [list]: A list of thermal objects
    """
    return [create_indexable_thermal(THERMAL_NAMING_RULE['psu thermals'], psu_index, CHASSIS_THERMAL_SYSFS_FOLDER, 1, presence_cb)]


def initialize_sfp_thermal(sfp_index):
    return [create_indexable_thermal(THERMAL_NAMING_RULE['sfp thermals'], sfp_index, CHASSIS_THERMAL_SYSFS_FOLDER, 1)]


def initialize_linecard_thermals(lc_name, lc_index):
    thermal_list = []
    rule = THERMAL_NAMING_RULE['linecard thermals']
    rule = copy.deepcopy(rule)
    rule['name'] = '{} {}'.format(lc_name, rule['name'])
    sysfs_folder = '/run/hw-management/lc{}/thermal'.format(lc_index)
    count = DeviceDataManager.get_gearbox_count('/run/hw-management/lc{}/config'.format(lc_index))
    for index in range(count):
        thermal_list.append(create_indexable_thermal(rule, index, sysfs_folder, index + 1))
    return thermal_list


def initialize_linecard_sfp_thermal(lc_name, lc_index, sfp_index):
    rule = THERMAL_NAMING_RULE['sfp thermals']
    rule = copy.deepcopy(rule)
    rule['name'] = '{} {}'.format(lc_name, rule['name'])
    sysfs_folder = '/run/hw-management/lc{}/thermal'.format(lc_index)
    return [create_indexable_thermal(rule, sfp_index, sysfs_folder, 1)]


def create_indexable_thermal(rule, index, sysfs_folder, position, presence_cb=None):
    index += rule.get('start_index', 1)
    name = rule['name'].format(index)
    temp_file = os.path.join(sysfs_folder, rule['temperature'].format(index))
    _check_thermal_sysfs_existence(temp_file)
    if 'high_threshold' in rule:
        high_th_file = os.path.join(sysfs_folder, rule['high_threshold'].format(index))
        _check_thermal_sysfs_existence(high_th_file)
    else:
        high_th_file = None
    if 'high_critical_threshold' in rule:
        high_crit_th_file = os.path.join(sysfs_folder, rule['high_critical_threshold'].format(index))
        _check_thermal_sysfs_existence(high_crit_th_file)
    else:
        high_crit_th_file = None
    if not presence_cb:
        return Thermal(name, temp_file, high_th_file, high_crit_th_file, position)
    else:
        return RemovableThermal(name, temp_file, high_th_file, high_crit_th_file, position, presence_cb)


def create_single_thermal(rule, sysfs_folder, position, presence_cb=None):
    temp_file = rule['temperature']
    default_present = rule.get('default_present', True)
    thermal_capability = DeviceDataManager.get_thermal_capability()

    if thermal_capability:
        if not thermal_capability.get(temp_file, default_present):
            return None
    elif not default_present:
        return None

    temp_file = os.path.join(sysfs_folder, temp_file)
    _check_thermal_sysfs_existence(temp_file)
    if 'high_threshold' in rule:
        high_th_file = os.path.join(sysfs_folder, rule['high_threshold'])
        _check_thermal_sysfs_existence(high_th_file)
    else:
        high_th_file = None
    if 'high_critical_threshold' in rule:
        high_crit_th_file = os.path.join(sysfs_folder, rule['high_critical_threshold'])
        _check_thermal_sysfs_existence(high_crit_th_file)
    else:
        high_crit_th_file = None
    name = rule['name']
    if not presence_cb:
        return Thermal(name, temp_file, high_th_file, high_crit_th_file, position)
    else:
        return RemovableThermal(name, temp_file, high_th_file, high_crit_th_file, position, presence_cb)


def _check_thermal_sysfs_existence(file_path):
    if not os.path.exists(file_path):
        logger.log_error('Thermal sysfs {} does not exist'.format(file_path))


class Thermal(ThermalBase):
    thermal_algorithm_status = False
    # Expect cooling level, used for caching the cooling level value before commiting to hardware
    expect_cooling_level = None
    # Expect cooling state
    expect_cooling_state = None
    # Last committed cooling level
    last_set_cooling_level = None
    last_set_cooling_state = None
    last_set_psu_cooling_level = None

    def __init__(self, name, temp_file, high_th_file, high_crit_th_file, position):
        """
        index should be a string for category ambient and int for other categories
        """
        super(Thermal, self).__init__()
        self.name = name
        self.position = position
        self.temperature = temp_file
        self.high_threshold = high_th_file
        self.high_critical_threshold = high_crit_th_file

    def get_name(self):
        """
        Retrieves the name of the device

        Returns:
            string: The name of the device
        """
        return self.name

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        value = utils.read_float_from_file(self.temperature, None, log_func=logger.log_info)
        return value / 1000.0 if (value is not None and value != 0) else None

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.high_threshold is None:
            return None
        value = utils.read_float_from_file(self.high_threshold, None, log_func=logger.log_info)
        return value / 1000.0 if (value is not None and value != 0) else None

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.high_critical_threshold is None:
            return None
        value = utils.read_float_from_file(self.high_critical_threshold, None, log_func=logger.log_info)
        return value / 1000.0 if (value is not None and value != 0) else None

    def get_position_in_parent(self):
        """
        Retrieves 1-based relative physical position in parent device
        Returns:
            integer: The 1-based relative physical position in parent device
        """
        return self.position

    def is_replaceable(self):
        """
        Indicate whether this device is replaceable.
        Returns:
            bool: True if it is replaceable.
        """
        return False

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
        if not force and cls.thermal_algorithm_status == status:
            return False

        cls.thermal_algorithm_status = status
        mode = "enabled" if status else "disabled"
        policy = "step_wise" if status else "user_space"
        for thermal_zone_folder in glob.iglob(THERMAL_ZONE_FOLDER_WILDCARD):
            policy_file = os.path.join(thermal_zone_folder, THERMAL_ZONE_POLICY_FILE)
            utils.write_file(policy_file, policy)
            mode_file = os.path.join(thermal_zone_folder, THERMAL_ZONE_MODE_FILE)
            utils.write_file(mode_file, mode)

        return True

    @classmethod
    def get_min_allowed_cooling_level_by_thermal_zone(cls):
        """Get min allowed cooling level according to thermal zone status:
            1. If temperature of all thermal zones is less than normal threshold, min allowed cooling level is
               $MIN_COOLING_LEVEL_FOR_NORMAL = 2
            2. If temperature of any thermal zone is greater than normal threshold, but no thermal zone temperature
               is greater than high threshold, min allowed cooling level is $MIN_COOLING_LEVEL_FOR_HIGH = 4
            3. Otherwise, there is no minimum allowed value and policy should not adjust cooling level
        Returns:
            int: minimum allowed cooling level
        """
        min_allowed = MIN_COOLING_LEVEL_FOR_NORMAL
        thermal_zone_present = False
        try:
            for thermal_zone_folder in glob.iglob(THERMAL_ZONE_FOLDER_WILDCARD):
                thermal_zone_present = True
                normal_thresh = utils.read_int_from_file(os.path.join(thermal_zone_folder, THERMAL_ZONE_NORMAL_THRESHOLD))
                current = utils.read_int_from_file(os.path.join(thermal_zone_folder, THERMAL_ZONE_TEMP_FILE))
                if current < normal_thresh - THERMAL_ZONE_HYSTERESIS:
                    continue

                hot_thresh = utils.read_int_from_file(os.path.join(thermal_zone_folder, THERMAL_ZONE_HIGH_THRESHOLD))
                if current < hot_thresh - THERMAL_ZONE_HYSTERESIS:
                    min_allowed = MIN_COOLING_LEVEL_FOR_HIGH
                else:
                    min_allowed = None
                    break
        except Exception as e:
            logger.log_error('Failed to get thermal zone status for {} - {}'.format(thermal_zone_folder, repr(e)))
            return None

        return min_allowed if thermal_zone_present else None

    @classmethod
    def check_module_temperature_trustable(cls):
        for file_path in glob.iglob(MODULE_TEMP_FAULT_WILDCARRD):
            fault = utils.read_int_from_file(file_path)
            if fault != 0:
                return 'untrust'
        return 'trust'

    @classmethod
    def get_min_amb_temperature(cls):
        fan_ambient_path = os.path.join(CHASSIS_THERMAL_SYSFS_FOLDER, 'fan_amb')
        port_ambient_path = os.path.join(CHASSIS_THERMAL_SYSFS_FOLDER, 'port_amb')

        try:
            fan_ambient_temp = utils.read_int_from_file(fan_ambient_path, raise_exception=True)
            port_ambient_temp = utils.read_int_from_file(port_ambient_path, raise_exception=True)
            return fan_ambient_temp if fan_ambient_temp < port_ambient_temp else port_ambient_temp
        except Exception as e:
            # Can't get ambient temperature, return maximum
            logger.log_error('Failed to get minimum ambient temperature, use pessimistic instead')
            return MAX_AMBIENT_TEMP

    @classmethod
    def set_cooling_level(cls, level):
        """
        Change cooling level. The input level should be an integer value [1, 10].
        1 means 10%, 2 means 20%, 10 means 100%.
        """
        if cls.last_set_cooling_level != level:
            utils.write_file(COOLING_STATE_PATH, level + 10, raise_exception=True)
            cls.last_set_cooling_level = level

    @classmethod
    def set_cooling_state(cls, state):
        """Change cooling state.
        Args:
            state (int): cooling state
        """
        if cls.last_set_cooling_state != state:
            utils.write_file(COOLING_STATE_PATH, state, raise_exception=True)
            cls.last_set_cooling_state = state

    @classmethod
    def get_cooling_level(cls):
        try:
            return utils.read_int_from_file(COOLING_STATE_PATH, raise_exception=True)
        except (ValueError, IOError) as e:
            raise RuntimeError("Failed to get cooling level - {}".format(e))

    @classmethod
    def set_expect_cooling_level(cls, expect_value):
        """During thermal policy running, cache the expect cooling level generated by policies. The max expect
           cooling level will be committed to hardware.
        Args:
            expect_value (int): Expected cooling level value
        """
        if cls.expect_cooling_level is None or cls.expect_cooling_level < expect_value:
            cls.expect_cooling_level = int(expect_value)

    @classmethod
    def commit_cooling_level(cls, thermal_info_dict):
        """Commit cooling level to hardware. This will affect system fan and PSU fan speed.
        Args:
            thermal_info_dict (dict): Thermal information dictionary
        """
        if cls.expect_cooling_level is not None:
            cls.set_cooling_level(cls.expect_cooling_level)

        if cls.expect_cooling_state is not None:
            cls.set_cooling_state(cls.expect_cooling_state)
        elif cls.expect_cooling_level is not None:
            cls.set_cooling_state(cls.expect_cooling_level)

        cls.expect_cooling_level = None
        # We need to set system fan speed here because kernel will automaticlly adjust fan speed according to cooling level and cooling state

        # Commit PSU fan speed with current state
        from .thermal_infos import ChassisInfo
        if ChassisInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ChassisInfo.INFO_NAME], ChassisInfo):
            cooling_level = cls.get_cooling_level()
            if cls.last_set_psu_cooling_level == cooling_level:
                return
            speed = cooling_level * 10
            chassis = thermal_info_dict[ChassisInfo.INFO_NAME].get_chassis()
            for psu in chassis.get_all_psus():
                for psu_fan in psu.get_all_fans():
                    psu_fan.set_speed(speed)
            cls.last_set_psu_cooling_level = cooling_level

    @classmethod
    def monitor_asic_themal_zone(cls):
        """This is a protection for asic thermal zone, if asic temperature is greater than hot threshold + THERMAL_ZONE_HYSTERESIS,
           and if cooling state is not MAX, we need enforce the cooling state to MAX
        """
        asic_temp = utils.read_int_from_file(os.path.join(THERMAL_ZONE_ASIC_PATH, THERMAL_ZONE_TEMP_FILE), raise_exception=True)
        hot_thresh = utils.read_int_from_file(os.path.join(THERMAL_ZONE_ASIC_PATH, THERMAL_ZONE_HOT_THRESHOLD), raise_exception=True)
        if asic_temp >= hot_thresh + THERMAL_ZONE_HYSTERESIS:
            cls.expect_cooling_state = MAX_COOLING_LEVEL
        else:
            cls.expect_cooling_state = None


class RemovableThermal(Thermal):
    def __init__(self, name, temp_file, high_th_file, high_crit_th_file, position, presence_cb):
        super(RemovableThermal, self).__init__(name, temp_file, high_th_file, high_crit_th_file, position)
        self.presence_cb = presence_cb

    def get_temperature(self):
        """
        Retrieves current temperature reading from thermal

        Returns:
            A float number of current temperature in Celsius up to nearest thousandth
            of one degree Celsius, e.g. 30.125
        """
        status, hint = self.presence_cb()
        if not status:
            logger.log_debug("get_temperature for {} failed due to {}".format(self.name, hint))
            return None
        return super(RemovableThermal, self).get_temperature()

    def get_high_threshold(self):
        """
        Retrieves the high threshold temperature of thermal

        Returns:
            A float number, the high threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        status, hint = self.presence_cb()
        if not status:
            logger.log_debug("get_high_threshold for {} failed due to {}".format(self.name, hint))
            return None
        return super(RemovableThermal, self).get_high_threshold()

    def get_high_critical_threshold(self):
        """
        Retrieves the high critical threshold temperature of thermal

        Returns:
            A float number, the high critical threshold temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        status, hint = self.presence_cb()
        if not status:
            logger.log_debug("get_high_critical_threshold for {} failed due to {}".format(self.name, hint))
            return None
        return super(RemovableThermal, self).get_high_critical_threshold()

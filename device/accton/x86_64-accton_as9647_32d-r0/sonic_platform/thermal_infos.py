from sonic_platform_base.sonic_thermal_control.thermal_info_base import ThermalPolicyInfoBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .thermal import logger
from enum import Enum

@thermal_json_object('fan_info')
class FanInfo(ThermalPolicyInfoBase):
    """
    Fan information needed by thermal policy
    """

    # Fan information name
    INFO_NAME = 'fan_info'

    def __init__(self):
        self._absence_fans = set()
        self._presence_fans = set()
        self._fault_fans = set()
        self._status_changed = False

    def collect(self, chassis):
        """
        Collect absence and presence fans.
        :param chassis: The chassis object
        :return:
        """
        self._status_changed = False
        for fan in chassis.get_all_fans():
            presence = fan.get_presence()
            status = fan.get_status()
            if presence and fan not in self._presence_fans:
                self._presence_fans.add(fan)
                self._status_changed = True
                if fan in self._absence_fans:
                    self._absence_fans.remove(fan)
            elif not presence and fan not in self._absence_fans:
                self._absence_fans.add(fan)
                self._status_changed = True
                if fan in self._presence_fans:
                    self._presence_fans.remove(fan)

            if not status and fan not in self._fault_fans:
                self._fault_fans.add(fan)
                self._status_changed = True
            elif status and fan in self._fault_fans:
                self._fault_fans.remove(fan)
                self._status_changed = True

    def get_absence_fans(self):
        """
        Retrieves absence fans
        :return: A set of absence fans
        """
        return self._absence_fans

    def get_presence_fans(self):
        """
        Retrieves presence fans
        :return: A set of presence fans
        """
        return self._presence_fans

    def get_fault_fans(self):
        """
        Retrieves fault fans
        :return: A set of fault fans
        """
        return self._fault_fans

    def is_status_changed(self):
        """
        Retrieves if the status of fan information changed
        :return: True if status changed else False
        """
        return self._status_changed


@thermal_json_object('psu_info')
class PsuInfo(ThermalPolicyInfoBase):
    """
    PSU information needed by thermal policy
    """
    INFO_NAME = 'psu_info'

    def __init__(self):
        self._absence_psus = set()
        self._presence_psus = set()
        self._status_changed = False

    def collect(self, chassis):
        """
        Collect absence and presence PSUs.
        :param chassis: The chassis object
        :return:
        """
        self._status_changed = False
        for psu in chassis.get_all_psus():
            if psu.get_presence() and psu.get_powergood_status() and psu not in self._presence_psus:
                self._presence_psus.add(psu)
                self._status_changed = True
                if psu in self._absence_psus:
                    self._absence_psus.remove(psu)
            elif (not psu.get_presence() or not psu.get_powergood_status()) and psu not in self._absence_psus:
                self._absence_psus.add(psu)
                self._status_changed = True
                if psu in self._presence_psus:
                    self._presence_psus.remove(psu)

    def get_absence_psus(self):
        """
        Retrieves presence PSUs
        :return: A set of absence PSUs
        """
        return self._absence_psus

    def get_presence_psus(self):
        """
        Retrieves presence PSUs
        :return: A set of presence fans
        """
        return self._presence_psus

    def is_status_changed(self):
        """
        Retrieves if the status of PSU information changed
        :return: True if status changed else False
        """
        return self._status_changed


@thermal_json_object('thermal_info')
class ThermalInfo(ThermalPolicyInfoBase):
    """
    Thermal information needed by thermal policy
    """
    from .thermal import Thermal
    from .chassis import PORT_END

    # Thermal information name
    INFO_NAME = 'thermal_info'

    class CoolingLevel(Enum):
        LEVEL_0 = 0
        LEVEL_1 = 1
        LEVEL_2 = 2
        LEVEL_3 = 3
        LEVEL_4 = 4
        LEVEL_5 = 5

    # Temperature deviation tolerance in degrees Celsius
    THERMAL_FAULT_SENSOR_TOLERANCE = 15

    NUM_CHASSIS_THERMALS = Thermal.NUMBER_OF_THERMALS
    NUM_XCVR_THERMALS = PORT_END
    NUM_THERMALS = NUM_CHASSIS_THERMALS + NUM_XCVR_THERMALS

    # Indices of `Thermal.py` instances corresponding to PCB temperature sensors.
    PCB_SENSOR_IDX_LIST = [0, 1, 2, 3, 4, 5, 6, 7]
    # Indices of `Thermal.py` instances corresponding to ASIC temperature sensors.
    ASIC_SENSOR_IDX_LIST = [8, 9, 10]
    # Indices of `Thermal.py` instances corresponding to CPU temperature sensors.
    CPU_SENSOR_IDX_LIST = [11]

    # Indices of `Thermal.py` instances used for detecting faulty sensor by average.
    AVG_SENSOR_IDX_LIST = [1, 2, 3]
    # Indices of `Thermal.py` instances used for thermal control (fan speed control and overheat detection).
    TC_SENSOR_IDX_LIST = AVG_SENSOR_IDX_LIST + ASIC_SENSOR_IDX_LIST + CPU_SENSOR_IDX_LIST

    # Indices of XCVR `Thermal.py` instances, starting after the PCB, ASIC, and CPU sensor indices.
    # Note: This list is not used in this file, it is used for testing purposes.
    XCVR_SENSOR_IDX_LIST = list(range(NUM_CHASSIS_THERMALS, NUM_THERMALS))

    class HysteresisMonitor:
        """
        A class per sensor to manage and update its hysteresis state

        Attributes:
            thresholds: This is a list containing 5 string elements, where each
                        element follows this format:
                        "low hysteresis threshold : high hysteresis threshold"
                        For example:
                            thresholds = ["19:31", "37:48", "45:53", "56:59", "NA:64"]
                            parameter                       value
                            ---------                       -----
                            low hysteresis threshold 1      19
                            high hysteresis threshold 1     31
                            low hysteresis threshold 2      37
                            high hysteresis threshold 2     48
                            low hysteresis threshold 3      45
                            high hysteresis threshold 3     53
                            low hysteresis threshold 4      56
                            high hysteresis threshold 4     59
                            low hysteresis threshold 5      NA
                            high hysteresis threshold 5     64
        """
        LOW_TH_IDX = 0
        HIGH_TH_IDX = 1

        def __init__(self, thresholds):
            self.thresholds = []
            for threshold in thresholds:
                low = threshold.split(':')[self.LOW_TH_IDX]
                if low != "NA":
                    low = int(low)

                high = threshold.split(':')[self.HIGH_TH_IDX]
                if high != "NA":
                    high = int(high)

                self.thresholds.append([low, high])

            self.cool_lvl_idx = 0

            # Track the current hysteresis state of each instance (True = high hyst, False = low hyst)
            self.hyst_state_list = [False] * len(thresholds)

        def get_cool_level(self):
            return self.cool_lvl_idx

        def update(self, value):
            """Update the hysteresis state based on the new input temperature value

            Args:
                value: integer value of the input temperature used to update the hysteresis state

            Returns:
                An integer representing the cool level index used to determine the actual fan speed
            """
            cool_lvl_idx = 0
            for idx, threshold in enumerate(self.thresholds):
                low = threshold[self.LOW_TH_IDX]
                high = threshold[self.HIGH_TH_IDX]

                # If the sensor is in the low state and the value crosses the high threshold
                if not self.hyst_state_list[idx] and isinstance(high, int) and value > high:
                    self.hyst_state_list[idx] = True
                # If the sensor is in the high state and the value crosses below or equals the low threshold
                elif self.hyst_state_list[idx] and isinstance(low, int) and value <= low:
                    self.hyst_state_list[idx] = False

                # Record the highest index crossed, which represents the cool level
                if self.hyst_state_list[idx]:
                    cool_lvl_idx = idx + 1

            self.cool_lvl_idx = cool_lvl_idx
            return cool_lvl_idx

    def __init__(self):
        from .thermal_device_data import DEVICE_DATA

        self._cool_lvl_idx = self.CoolingLevel.LEVEL_0.value

        self._thermal_list = None
        self._temp_list = None

        self._tc_temps_changed = False

        self._faulty_sensor_average_detected = False
        self._faulty_sensor_invalid_detected = False
        self._faulty_sensors = []
        self._faulty_average = None

        self._warn_oh = False
        self._warn_oh_sensor_idx_list = []

        self._crit_oh = False
        self._crit_oh_sensor_idx_list = []

        # Create a list of HysteresisMonitor classes, one per sensor, to track
        # the threshold state of each sensor.
        self.hyst_monitor_list = []
        for idx in self.TC_SENSOR_IDX_LIST:
            self.hyst_monitor_list.append(self.HysteresisMonitor(DEVICE_DATA['thresholds'][idx]))

    def collect(self, chassis):
        """
        Collect thermal sensor temperature change status
        :param chassis: The chassis object
        :return:
        """
        self._tc_temps_changed = False

        self._faulty_sensor_average_detected = False
        self._faulty_sensor_invalid_detected = False
        self._faulty_average = None

        self._warn_oh = False
        self._warn_oh_sensor_idx_list = []

        self._crit_oh = False
        self._crit_oh_sensor_idx_list = []

        # Collect all thermal class instances and temperature samples
        self._thermal_list = chassis.get_all_thermals()
        temp_list = [thermal.get_temperature() for thermal in self._thermal_list]

        # Check whether the temperature values used for cooling level calculation have changed
        if self._temp_list is None:
            self._tc_temps_changed = True
        else:
            for idx in self.TC_SENSOR_IDX_LIST:
                if self._temp_list[idx] != temp_list[idx]:
                    self._tc_temps_changed = True

        # Detect thermal faulty sensor based on invalid-sample condition
        if self._tc_temps_changed:
            self._faulty_sensors = []
            for idx in self.TC_SENSOR_IDX_LIST:
                if not isinstance(temp_list[idx], float):
                    self._faulty_sensor_invalid_detected = True
                    self._faulty_sensors.append(idx)

        if not self._faulty_sensor_invalid_detected and self._tc_temps_changed:
            try:
                # Determine the maximum cooling level index among all HysteresisMonitor instances
                cool_lvl_idx = self.CoolingLevel.LEVEL_0.value
                for idx, sensor_idx in enumerate(self.TC_SENSOR_IDX_LIST):
                    cool_lvl_idx = max(cool_lvl_idx, self.hyst_monitor_list[idx].update(temp_list[sensor_idx]))

                # Log and save the cooling level index
                if cool_lvl_idx != self._cool_lvl_idx:
                    logger.log_notice("Cooling level index has changed from {} to {}".format(
                        self._cool_lvl_idx, cool_lvl_idx))
                    self._cool_lvl_idx = cool_lvl_idx

                # Detect thermal warning/critical overheat
                for idx, sensor_idx in enumerate(self.TC_SENSOR_IDX_LIST):
                    cool_level = self.hyst_monitor_list[idx].get_cool_level()
                    if cool_level == self.CoolingLevel.LEVEL_5.value:
                        self._crit_oh_sensor_idx_list.append(sensor_idx)
                        self._crit_oh = True
                    elif cool_level == self.CoolingLevel.LEVEL_4.value:
                        self._warn_oh_sensor_idx_list.append(sensor_idx)
                        self._warn_oh = True
            except Exception as e:
                logger.log_error("Failure in cooling level index calculation: {}".format(str(e)))

            try:
                # Detect thermal faulty sensor based on average-value condition
                avg_temp_list = [temp_list[idx] for idx in self.AVG_SENSOR_IDX_LIST]
                avg_temp = round(sum(avg_temp_list) / len(avg_temp_list), 1)
                self._faulty_sensors = []
                for idx in self.AVG_SENSOR_IDX_LIST:
                    if abs(temp_list[idx] - avg_temp) > self.THERMAL_FAULT_SENSOR_TOLERANCE:
                        self._faulty_sensor_average_detected = True
                        self._faulty_sensors.append(idx)
                        self._faulty_average = avg_temp
            except Exception as e:
                logger.log_error("Failure in average temperature calculation: {}".format(str(e)))

        self._temp_list = temp_list

    def get_critical_overheat_sensor_idx_list(self):
        """
        Retrieves a list of sensor indices that caused the critical overheat.
        :return: List of sensor indices.
        """
        return self._crit_oh_sensor_idx_list

    def is_critical_overheat(self):
        """
        Get an indication if a critical overheat condition has occurred.
        :return: True if a critical overheat was detected, otherwise False
        """
        return self._crit_oh

    def get_warning_overheat_sensor_idx_list(self):
        """
        Retrieves a list of sensor indices that caused the warning overheat.
        :return: List of sensor indices.
        """
        return self._warn_oh_sensor_idx_list

    def is_warning_overheat(self):
        """
        Get an indication if a warning overheat condition has occurred.
        :return: True if a warning overheat was detected, otherwise False
        """
        return self._warn_oh

    def is_tc_temperatures_changed(self):
        """
        Get an indication of whether thermal sensor samples have changed among
        the sensors involved in the fan speed control logic.
        :return: True if any temperatures have changed, otherwise False
        """
        return self._tc_temps_changed

    def get_thermal_list(self):
        """
        Retrieves a list of thermal.
        :return: List of thermal class instances.
        """
        return self._thermal_list

    def get_temperatures(self):
        """
        Retrieves a list of all temperature samples.
        :return: List of all temperature samples.
        """
        return self._temp_list

    def get_cooling_level_idx(self):
        """
        Retrieves the cooling level index.
        :return: Integer of cooling level index.
        """
        return self._cool_lvl_idx

    def is_faulty_sensor_invalid_detected(self):
        """
        Get an indication if a faulty sensor has been detected based on invalid-sample condition.
        :return: True if a faulty sensor is found, otherwise False
        """
        return self._faulty_sensor_invalid_detected

    def is_faulty_sensor_average_detected(self):
        """
        Get an indication if a faulty sensor has been detected based on average-value condition.
        :return: True if a faulty sensor is found, otherwise False
        """
        return self._faulty_sensor_average_detected

    def get_faulty_sensors(self):
        """
        Retrieves a list of all faulty sensor indices.
        :return: List of all faulty sensor indices.
        """
        return self._faulty_sensors

    def get_faulty_average(self):
        """
        Retrieves the average temperature of the faulty sensors.
        :return: The average temperature of the faulty sensors.
        """
        return self._faulty_average

@thermal_json_object('chassis_info')
class ChassisInfo(ThermalPolicyInfoBase):
    """
    Chassis information needed by thermal policy
    """
    INFO_NAME = 'chassis_info'

    def __init__(self):
        self._chassis = None

    def collect(self, chassis):
        """
        Collect platform chassis.
        :param chassis: The chassis object
        :return:
        """
        self._chassis = chassis

    def get_chassis(self):
        """
        Retrieves platform chassis object
        :return: A platform chassis object.
        """
        return self._chassis

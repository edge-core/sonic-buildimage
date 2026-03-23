from sonic_platform_base.sonic_thermal_control.thermal_condition_base import ThermalPolicyConditionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .thermal import logger

class FanCondition(ThermalPolicyConditionBase):
    def get_fan_info(self, thermal_info_dict):
        from .thermal_infos import FanInfo
        fan_info_obj = None
        if FanInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[FanInfo.INFO_NAME], FanInfo):
            fan_info_obj = thermal_info_dict[FanInfo.INFO_NAME]
        else:
            logger.log_error("Failed to get fans information")
        return fan_info_obj

class ThermalCondition(ThermalPolicyConditionBase):
    def get_thermal_info(self, thermal_info_dict):
        from .thermal_infos import ThermalInfo
        thermal_info_obj = None
        if ThermalInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ThermalInfo.INFO_NAME], ThermalInfo):
            thermal_info_obj = thermal_info_dict[ThermalInfo.INFO_NAME]
        else:
            logger.log_error("Failed to get thermals information")
        return thermal_info_obj


@thermal_json_object('fan.any.absence')
class AnyFanAbsenceCondition(FanCondition):
    def is_match(self, thermal_info_dict):
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        return len(fan_info_obj.get_absence_fans()) > 0 if fan_info_obj else False


@thermal_json_object('fan.all.presence')
class AllFanPresenceCondition(FanCondition):
    def is_match(self, thermal_info_dict):
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        return len(fan_info_obj.get_absence_fans()) == 0 if fan_info_obj else False


@thermal_json_object('fan.any.fault')
class AnyFanFaultCondition(FanCondition):
    def is_match(self, thermal_info_dict):
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        return len(fan_info_obj.get_fault_fans()) > 0 if fan_info_obj else False


@thermal_json_object('fan.all.good')
class AllFanGoodCondition(FanCondition):
    def is_match(self, thermal_info_dict):
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        return len(fan_info_obj.get_fault_fans()) == 0 if fan_info_obj else False


@thermal_json_object('thermal.any.warning')
class ThermalWarningCondition(ThermalCondition):
    """
    A thermal condition class that checks and indicates whether there is a
    thermal warning overheat (chassis or XCVR).
    """
    def is_match(self, thermal_info_dict):
        result = False
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            result = thermal_info_obj.is_warning_overheat() or thermal_info_obj.is_xcvr_warning_overheat()
        return result


@thermal_json_object('thermal.any.critical')
class ThermalCriticalCondition(ThermalCondition):
    """
    A thermal condition class that checks and indicates whether there is a
    thermal critical overheat (chassis or XCVR).
    """
    def is_match(self, thermal_info_dict):
        result = False
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            result = thermal_info_obj.is_critical_overheat() or thermal_info_obj.is_xcvr_critical_overheat()
        return result


@thermal_json_object('thermal.any.change')
class ThermalAnyChangeCondition(ThermalCondition, FanCondition):
    """
    A thermal condition class that checks and indicates whether there is a
    temperature change among the sensors participating in fan speed control logic,
    or a fan status change.
    """
    def is_match(self, thermal_info_dict):
        result = False
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        fan_info_obj = self.get_fan_info(thermal_info_dict)
        if thermal_info_obj and fan_info_obj:
            tc_temperatures_changed = thermal_info_obj.is_tc_temperatures_changed()
            fan_status_changed = fan_info_obj.is_status_changed()
            if tc_temperatures_changed or fan_status_changed:
                logger.log_info("Thermal status changed, temperatures: {}, fans: {}".format(
                    thermal_info_obj.get_temperatures(), fan_status_changed))
                result = True
        return result


@thermal_json_object('thermal.faulty.sensor')
class ThermalFaultySensorCondition(ThermalCondition):
    """
    A thermal condition class that checks and indicates whether a faulty temperature
    sensor is detected.
    """
    def is_match(self, thermal_info_dict):
        result = False
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            thermal_list = thermal_info_obj.get_thermal_list()
            faulty_sensor_idxs = thermal_info_obj.get_faulty_sensors()
            temp_list = thermal_info_obj.get_temperatures()

            if thermal_info_obj.is_faulty_sensor_invalid_detected():
                for idx in faulty_sensor_idxs:
                    logger.log_error("Thermal faulty sensor detected due to an invalid sample on `{}` sensor: "
                    "value={}".format(thermal_list[idx].get_name(), temp_list[idx]))
                result = True
            elif thermal_info_obj.is_faulty_sensor_average_detected():
                avg_temp = thermal_info_obj.get_faulty_average()
                avg_temp_list = [temp_list[idx] for idx in thermal_info_obj.AVG_SENSOR_IDX_LIST]
                for idx in faulty_sensor_idxs:
                    logger.log_error("Thermal faulty sensor detected on `{}` sensor due to average deviation: "
                    "value={}, samples={}, average={}".format(
                        thermal_list[idx].get_name(), temp_list[idx], avg_temp_list, avg_temp))
                result = True
        return result

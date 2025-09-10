from sonic_platform_base.sonic_thermal_control.thermal_condition_base import ThermalPolicyConditionBase
from sonic_platform_base.sonic_thermal_control.thermal_json_object import thermal_json_object
from .thermal import logger

class FanCondition(ThermalPolicyConditionBase):
    def get_fan_info(self, thermal_info_dict):
        from .thermal_infos import FanInfo
        if FanInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[FanInfo.INFO_NAME], FanInfo):
            return thermal_info_dict[FanInfo.INFO_NAME]
        else:
            return None


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


class PsuCondition(ThermalPolicyConditionBase):
    def get_psu_info(self, thermal_info_dict):
        from .thermal_infos import PsuInfo
        if PsuInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[PsuInfo.INFO_NAME], PsuInfo):
            return thermal_info_dict[PsuInfo.INFO_NAME]
        else:
            return None


class ThermalCondition(ThermalPolicyConditionBase):
    def get_thermal_info(self, thermal_info_dict):
        from .thermal_infos import ThermalInfo
        if ThermalInfo.INFO_NAME in thermal_info_dict and isinstance(thermal_info_dict[ThermalInfo.INFO_NAME], ThermalInfo):
            return thermal_info_dict[ThermalInfo.INFO_NAME]
        else:
            return None


@thermal_json_object('thermal.over.high_critical_threshold')
class ThermalOverHighCriticalCondition(ThermalCondition):
    def is_match(self, thermal_info_dict):
        thermal_info_obj = self.get_thermal_info(thermal_info_dict)
        if thermal_info_obj:
            res = thermal_info_obj.is_over_high_critical_threshold()
            if res == True:
                logger.log_notice("Thermal policy condition 'thermal.over.high_critical_threshold' was matched")
            return res
        else:
            return False


@thermal_json_object('thermal.any.change')
class MinCoolingLevelChangeCondition(ThermalPolicyConditionBase):
    trust_state = None
    previous_temperatures = None
    temperatures = None
    
    def is_match(self, thermal_info_dict):
        from .thermal import Thermal

        trust_state = Thermal.check_module_temperature_trustable()
        MinCoolingLevelChangeCondition.temperatures = Thermal.get_temperatures()

        change_cooling_level = False
        if trust_state != MinCoolingLevelChangeCondition.trust_state:
            MinCoolingLevelChangeCondition.trust_state = trust_state
            change_cooling_level = True

        if MinCoolingLevelChangeCondition.previous_temperatures is not None:
            indX = 0
            for indX in range(3):
                if MinCoolingLevelChangeCondition.temperatures[indX] != MinCoolingLevelChangeCondition.previous_temperatures[indX]:
                    change_cooling_level = True
        else:
            change_cooling_level = True

        MinCoolingLevelChangeCondition.previous_temperatures = MinCoolingLevelChangeCondition.temperatures
        logger.log_debug("MinCoolingLevelChangeCondition: temperatures {} change_cooling_level {}".format(
            str(MinCoolingLevelChangeCondition.temperatures), change_cooling_level))
        return change_cooling_level

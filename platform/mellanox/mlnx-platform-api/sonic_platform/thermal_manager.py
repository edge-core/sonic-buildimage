from sonic_platform_base.sonic_thermal_control.thermal_manager_base import ThermalManagerBase
from .thermal_actions import *  # lgtm [py/polluting-import]
from .thermal_conditions import *  # lgtm [py/polluting-import]
from .thermal_infos import *  # lgtm [py/polluting-import]
from .thermal import logger, MAX_COOLING_LEVEL, Thermal


class ThermalManager(ThermalManagerBase):
    @classmethod
    def deinitialize(cls):
        """
        Destroy thermal manager, including any vendor specific cleanup. The default behavior of this function
        is a no-op.
        :return:
        """
        cls.start_thermal_control_algorithm()

    @classmethod
    def start_thermal_control_algorithm(cls):
        """
        Start thermal control algorithm

        Returns:
            bool: True if set success, False if fail.
        """
        Thermal.set_thermal_algorithm_status(True)

    @classmethod
    def stop_thermal_control_algorithm(cls):
        """
        Stop thermal control algorithm

        Returns:
            bool: True if set success, False if fail.
        """
        Thermal.set_thermal_algorithm_status(False)

    @classmethod
    def run_policy(cls, chassis):
        if not cls._policy_dict:
            return

        try:
            cls._collect_thermal_information(chassis)
        except Exception as e:
            logger.log_error('Failed to collect thermal information {}'.format(repr(e)))
            Thermal.set_expect_cooling_level(MAX_COOLING_LEVEL)
            Thermal.commit_cooling_level(cls._thermal_info_dict)
            return

        for policy in cls._policy_dict.values():
            try:
                if policy.is_match(cls._thermal_info_dict):
                    policy.do_action(cls._thermal_info_dict)
            except Exception as e:
                logger.log_error('Failed to run thermal policy {} - {}'.format(policy.name, repr(e)))
                # In case there is an exception, we put cooling level to max value
                Thermal.set_expect_cooling_level(MAX_COOLING_LEVEL)

        Thermal.commit_cooling_level(cls._thermal_info_dict)


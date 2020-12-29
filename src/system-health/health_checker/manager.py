class HealthCheckerManager(object):
    """
    Manage all system health checkers and system health configuration.
    """
    STATE_BOOTING = 'booting'
    STATE_RUNNING = 'running'
    boot_timeout = None

    def __init__(self):
        self._checkers = []
        self._state = self.STATE_BOOTING

        from .config import Config
        self.config = Config()
        self.initialize()

    def initialize(self):
        """
        Initialize the manager. Create service checker and hardware checker by default.
        :return:
        """
        from .service_checker import ServiceChecker
        from .hardware_checker import HardwareChecker
        self._checkers.append(ServiceChecker())
        self._checkers.append(HardwareChecker())

    def check(self, chassis):
        """
        Load new configuration if any and perform the system health check for all existing checkers.
        :param chassis: A chassis object.
        :return: A tuple. The first element indicate the status of the checker; the second element is a dictionary that
        contains the status for all objects that was checked.
        """
        from .health_checker import HealthChecker
        HealthChecker.summary = HealthChecker.STATUS_OK
        stats = {}
        self.config.load_config()
        # check state first to avoid user change boot timeout in configuration file
        # after finishing system boot
        if self._state == self.STATE_BOOTING and self._is_system_booting():
            self._set_system_led(chassis, self.config, 'booting')
            return self._state, stats

        for checker in self._checkers:
            self._do_check(checker, stats)

        if self.config.user_defined_checkers:
            from .user_defined_checker import UserDefinedChecker
            for udc in self.config.user_defined_checkers:
                checker = UserDefinedChecker(udc)
                self._do_check(checker, stats)

        led_status = 'normal' if HealthChecker.summary == HealthChecker.STATUS_OK else 'fault'
        self._set_system_led(chassis, self.config, led_status)

        return self._state, stats

    def _do_check(self, checker, stats):
        """
        Do check for a particular checker and collect the check statistic.
        :param checker: A checker object.
        :param stats: Check statistic.
        :return:
        """
        try:
            checker.check(self.config)
            category = checker.get_category()
            info = checker.get_info()
            if category not in stats:
                stats[category] = info
            else:
                stats[category].update(info)
        except Exception as e:
            from .health_checker import HealthChecker
            error_msg = 'Failed to perform health check for {} due to exception - {}'.format(checker, repr(e))
            entry = {str(checker): {
                HealthChecker.INFO_FIELD_OBJECT_STATUS: HealthChecker.STATUS_NOT_OK,
                HealthChecker.INFO_FIELD_OBJECT_MSG: error_msg
            }}
            if 'Internal' not in stats:
                stats['Internal'] = entry
            else:
                stats['Internal'].update(entry)

    def _is_system_booting(self):
        from .utils import get_uptime
        uptime = get_uptime()
        if not self.boot_timeout:
            self.boot_timeout = self.config.get_bootup_timeout()
        booting = uptime < self.boot_timeout
        if not booting:
            self._state = self.STATE_RUNNING
        return booting

    def _set_system_led(self, chassis, config, status):
        try:
            chassis.set_status_led(config.get_led_color(status))
        except NotImplementedError:
            print('chassis.set_status_led is not implemented')
        except Exception as e:
            print('Failed to set system led due to - {}'.format(repr(e)))

from i2c_health_mgr.i2c_bus_checker import I2CBusChecker
from i2c_health_mgr.i2c_devices_scanner import I2CDevicesScanner, execute_os_cmd
from i2c_health_mgr.i2c_health_msgs import get_i2c_health_msg

import i2c_health_mgr.i2c_platform_api as i2c_platform_api

I2C_PMON_SERVICE_LIST = [
            'pmon:psud',
            'pmon:xcvrd',
            'syseepromd',
            'thermalctld',
            'sensord'
        ]

# Stop I2C Services CMDs
STOP_PLAT_SERVICE = "sudo systemctl stop {}"
STOP_PMON_SERVICE = "docker exec pmon supervisorctl stop {}"
STOP_PMON_SENSORD = "docker exec pmon service sensord stop"

# Start I2C Services CMDs
START_PLAT_SERVICE = "sudo systemctl start {}"
START_PMON_SERVICE = "docker exec pmon supervisorctl start {}"
START_PMON_SENSORD = "docker exec pmon service sensord start"




class I2CHealthManager:


    def __init__(self, logger):
        self.plat_api = i2c_platform_api.I2CPlatformAPI(logger)
        self.i2c_bus_checker = I2CBusChecker(logger, self.plat_api)
        self.i2c_devices_checker = I2CDevicesScanner(logger, self.i2c_bus_checker, self.plat_api)
        self.i2c_plat_services = self.plat_api.get_i2c_platform_service_list()
        self.i2c_pmon_services = I2C_PMON_SERVICE_LIST
        self.logger = logger
        self.sel, self.context = self.i2c_devices_checker.subscribe_device_removal_event()


    def is_bus_lock(self):
        return self.i2c_bus_checker.is_bus_lock()


    def stop_i2c_services(self):
        """
        Stops all I2C-related services on the system.

        This function performs the following steps:
        1. Stops the PMON I2C services, with the exception of the 'sensord' service, which is handled separately.
        2. Stops the Host platform I2C services.

        If any service fails to stop, the function immediately returns False.
        Returns True if all services are successfully stopped.

        Returns:
            bool: True if all services are stopped successfully, False otherwise.
        """

        for service in self.i2c_pmon_services:
            cmd = STOP_PMON_SENSORD if service == 'sensord' else STOP_PMON_SERVICE.format(service)

            msg = get_i2c_health_msg(19) # 019: cmd to stop i2c daemon service
            self.logger.log_notice(msg.format(cmd))
            if not execute_os_cmd(cmd):
                msg = get_i2c_health_msg(20) # 020: cmd to stop i2c daemon service
                self.logger.log_error(msg.format(cmd))
                return False


        for service in self.i2c_plat_services:
            cmd = STOP_PLAT_SERVICE.format(service)

            msg = get_i2c_health_msg(19) # 019: cmd to stop i2c daemon service
            self.logger.log_notice(msg.format(cmd))
            if not execute_os_cmd(cmd):
                msg = get_i2c_health_msg(20) # 020: cmd to stop i2c daemon service
                self.logger.log_error(msg.format(cmd))
                return False

        return True


    def start_i2c_services(self):
        """
        Starts all I2C-related services on the system.

        This function performs the following steps:
        1. Starts the Host platform I2C services.
        2. Starts the PMON I2C services, with the 'sensord' service handled separately.

        If any service fails to start, the function immediately returns False.
        Returns True if all services are successfully started.

        Returns:
            bool: True if all services are started successfully, False otherwise.
        """

        for service in self.i2c_plat_services:
            cmd = START_PLAT_SERVICE.format(service)
            msg = get_i2c_health_msg(21) # 021: cmd to start i2c daemon service
            self.logger.log_notice(msg.format(cmd))
            if not execute_os_cmd(cmd):
                msg = get_i2c_health_msg(22) # 022: cmd to start i2c daemon service
                self.logger.log_error(msg.format(cmd))
                return False


        for service in self.i2c_pmon_services:
            cmd = START_PMON_SENSORD if service == 'sensord' else START_PMON_SERVICE.format(service)
            msg = get_i2c_health_msg(21) # 021: cmd to start i2c daemon service
            self.logger.log_notice(msg.format(cmd))
            if not execute_os_cmd(cmd):
                msg = get_i2c_health_msg(22) # 022: cmd to start i2c daemon service
                self.logger.log_error(msg.format(cmd))
                return False

        return True


    def reset_all_mux(self):
        return self.plat_api.reset_all_mux()


    def set_all_fans_full_speed(self):
        return self.plat_api.set_all_fans_full_speed()


    def scan_faulty_devices(self):
        self.i2c_devices_checker.i2c_faulty_devices_scan()


    def handle_device_removal_event(self, stop_event):
        self.i2c_devices_checker.handle_device_removal_event(self.sel, self.context, stop_event)


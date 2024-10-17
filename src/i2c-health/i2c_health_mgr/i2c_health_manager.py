from i2c_health_mgr.i2c_bus_checker import I2CBusChecker
from i2c_health_mgr.i2c_devices_scanner import I2CDevicesScanner, execute_os_cmd

import i2c_platform_api

I2C_PMON_SERVICE_LIST = [
            'pmon:psud',
            'pmon:xcvrd',
            'pmon:xcvrd',
            'sensord'
        ]

# Stop I2C Services CMDs
STOP_PLAT_SERVICE = 'sudo systemctl stop'
STOP_PMON_SENSORD = 'docker exec pmon service sensord stop'
STOP_PMON_SERVICE = 'docker exec pmon supervisorctl stop'

# Start I2C Services CMDs
START_PLAT_SERVICE = 'sudo systemctl start'
START_PMON_SERVICE = 'docker exec pmon supervisorctl start'
START_PMON_SENSORD = 'docker exec pmon service sensord start'




class I2CHealthManager:


    def __init__(self, logger):
        self.plat_api = i2c_platform_api.I2CPlatformAPI()
        self.i2c_bus_checker = I2CBusChecker(logger, self.plat_api)
        self.i2c_devices_checker = I2CDevicesScanner(logger, self.i2c_bus_checker, self.plat_api)
        self.i2c_plat_services = self.plat_api.get_i2c_platform_service_list()
        self.i2c_pmon_services = I2C_PMON_SERVICE_LIST
        self.logger=logger


    def is_bus_lock(self):
        return self.i2c_bus_checker.is_bus_lock()


    def stop_i2c_services(self):
        # Step1: Stop PMON I2C services
        for service in self.i2c_pmon_services:
            if service != 'sensord':
                cmd = STOP_PMON_SERVICE.format(service)
            else:
                cmd = STOP_PMON_SENSORD

            ret = execute_os_cmd(cmd)
            if ret is False:
                return False

        # Step2: Stop Host platform I2C services
        for service in self.i2c_plat_services:
            cmd = STOP_PLAT_SERVICE.format(service)

            ret = execute_os_cmd(cmd)

            if ret is False:
                return False

        return True

    def start_i2c_services(self):
        # Step1: Start Host platform I2C services
        for service in self.i2c_plat_services:
            cmd = START_PLAT_SERVICE.format(service)
            ret = execute_os_cmd(cmd)

            if ret is False:
                return False


        # Step2: Star PMON I2C services
        for service in self.i2c_pmon_services:
            if service != 'sensord':
                cmd = START_PMON_SERVICE.format(service)
            else:
                cmd = START_PMON_SENSORD

            ret = execute_os_cmd(cmd)
            if ret is False:
                return False

        return True


    def reset_all_mux(self):
        return self.plat_api.reset_all_mux()


    def set_all_fans_full_speed(self):
        return self.plat_api.set_all_fans_full_speed()

    def scan_faulty_devices(self):
        self.i2c_devices_checker.i2c_faulty_devices_scan()


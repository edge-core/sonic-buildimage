from i2c_health_mgr.i2c_bus_checker import I2CBusChecker
from i2c_health_mgr.i2c_faulty_devices_scanner import I2CFaultyDevicesScanner

class I2CHealthMgr:


    def __init__(self):
        self.i2c_bus_checker = I2CBusChecker()
        self.i2c_devices_checker = I2CFaultyDevicesScanner()


    def is_bus_lock(self):
        return self.i2c_bus_checker.is_bus_lock()


    def stop_i2c_daemons(self):
        pass


    def start_i2c_daemons(self):
        pass


    def reset_mux(self):
        pass


    def set_all_fans_full_speed(self):
        pass

    def scan_faulty_devices(self):
        self.fault_devices_scanner.faulty_devices_scan()


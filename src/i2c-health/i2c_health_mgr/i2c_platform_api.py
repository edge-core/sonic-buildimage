import sonic_platform.platform

class I2CPlatformAPI:


    def __init__(self):
        self.platform = sonic_platform.platform.Platform()
        self.chassis = self.platform.get_chassis()


    def get_all_i2c_region_list(self):
        if self.chassis is not None:
            try:
                return self.chassis.get_all_i2c_region_list()
            except:
                return None

        return None


    def get_i2c_daemons(self):
        if self.chassis is not None:
            try:
                return self.chassis.get_i2c_daemons()
            except:
                return None

        return None


    def reset_all_mux(self):
        if self.chassis is not None:
            self.chassis.reset_i2c_mux()


    def set_all_fans_full_speed(self):
        pass


    def set_i2c_faulty_device(self, bus, device_addr, faulty):
        pass


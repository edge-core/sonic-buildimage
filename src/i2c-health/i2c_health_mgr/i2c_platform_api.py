import logging

class I2CPlatformAPI:
    def __init__(self):
        self.chassis = None
        try:
            import sonic_platform.platform
            self.chassis = sonic_platform.platform.Platform().get_chassis()
        except Exception as e:
            logging.warning("Failed to load chassis due to {}".format(repr(e)))


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
        """
        bus: I2C bus id
        device_addr: I2C device address
        device_enabled: True if this is a faulty device else False
        """
        if self.chassis is not None:
            try:
                return self.chassis.set_i2c_faulty_device(bus, device_addr, faulty)
            except:
                return None

        return None


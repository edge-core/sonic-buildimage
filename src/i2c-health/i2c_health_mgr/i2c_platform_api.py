
class I2CPlatformAPI:
    def __init__(self, logger):
        self.chassis = None
        try:
            import sonic_platform.platform
            self.chassis = sonic_platform.platform.Platform().get_chassis()
        except Exception as e:
            logger.log_error("Failed to load chassis due to {}".format(repr(e)))


    def get_all_i2c_region_list(self):
        if self.chassis is not None:
            try:
                return self.chassis.get_all_i2c_region_list()
            except:
                return {}

        return {}

    def get_i2c_representative_dev_list(self):
        if self.chassis is not None:
            try:
                return self.chassis.representative_devices_get()
            except:
                return []

        return []

    def get_i2c_platform_service_list(self):
        if self.chassis is not None:
            try:
                return self.chassis.get_platform_service_list()
            except:
                return []

        return []


    def reset_all_mux(self):
        if self.chassis is not None:
            try:
                return self.chassis.reset_i2c_mux()
            except:
                return False

        return False


    def set_all_fans_full_speed(self):
        if self.chassis is not None:
            try:
                return self.chassis.set_all_fan_full_speed()
            except:
                return False

        return False


    def set_i2c_faulty_device(self, bus, device_addr, faulty):
        """
        bus: I2C bus id
        device_addr: I2C device address
        faulty: True if this is a faulty device else False
        """
        if self.chassis is not None:
            try:
                return self.chassis.set_i2c_faulty_device(bus, device_addr, faulty)
            except:
                return False

        return False

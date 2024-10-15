class I2CDeviceEntity:
    def __init__(self, name, bus, device_addr, register_addr):
        self.name = name
        self.bus = bus
        self.device_addr = device_addr
        self.register_addr = register_addr

    def get_name(self):
        return self.name

    def get_bus(self):
        return self.bus

    def get_device_addr(self):
        return self.device_addr

    def get_register_addr(self):
        return self.register_addr

    def get_i2c_address_path(self):
        return "{}-00{}".format(self.bus, self.device_addr[2:])

    def __str__(self):
        return "Name: {}, Bus: {}, Device address: {}, Register address: {}".format(self.name, self.bus, self.device_addr, self.register_addr)
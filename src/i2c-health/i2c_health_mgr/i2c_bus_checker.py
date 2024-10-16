from i2c_platform_api import I2CPlatformAPI
from i2c_device_entity import I2CDeviceEntity
import subprocess
import logging


class I2CBusChecker:
    def __init__(self, logger):
        self.logger = logger
        self.i2c_platform_api = I2CPlatformAPI()
        self.i2c_dev_list = self.i2c_platform_api.get_i2c_representative_dev_list()
        self.i2c_representative_list = _wrapper_representative_devices_list()

    def _wrapper_representative_devices_list(self):
        representative_list = []
        try:
            for device in self.i2c_dev_list:
                representative_list.append(
                    I2CDeviceEntity(
                        device['name'],
                        device['bus'],
                        device['device_addr'],
                        device['register_addr']
                    )
                )
        except:
            self.logger.error("Init representative devices list error.")
            pass
        return representative_list
    
    def i2c_representative_list_get(self):
        ''' The list data is like:
            [
                {'name': 'PCA9548', 'bus': '0', 'device_addr': '0x77', 'register_addr': '0x0'},
                {'name': 'CPLD4'  , 'bus': '0', 'device_addr': '0x65', 'register_addr': '0x0'},
                {'name': 'EEPROM' , 'bus': '0', 'device_addr': '0x57', 'register_addr': '0x0'}
            ]
        '''
        return self.i2c_dev_list

    def is_bus_lock(self, retry_count=3):
        all_failed = True
        for device in self.i2c_representative_list:
            name = device.get_name()
            bus = device.get_bus()
            device_addr = device.get_device_addr()
            register_addr = device.get_register_addr()
            cmd = ['sudo', 'i2cget', '-f', '-y', str(bus), device_addr, register_addr]
            self.logger.info('I2C cmd {}'.format(cmd))

            attempt = 0

            while attempt < retry_count:
                attempt += 1
                try:
                    result = subprocess.run(cmd, capture_output=True, text=True)
                    return_code = result.returncode

                    if return_code == 0:
                        self.logger.info('{}: I2C get successful on attempt {}/{}.'.format(device, attempt, retry_count))
                        all_failed = False  # At least one device succeeded
                        return all_failed 
                    else:
                        print(f"{device}: I2C get failed, Return Code: {return_code}")
                        self.logger.warning('{}: I2C get failed on attempt {}/{}.'.format(device, attempt, retry_count))

                except Exception as e:
                    self.logger.warning('{}: Error I2C get on attempt {}/{}.'.format(device, attempt, retry_count))

        if all_failed:
            self.logger.warning('I2C bus lock!')
        return all_failed

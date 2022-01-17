try:
    from threading import Timer
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")
    
class ThermalManager():
    def __init__(self, polling_time = 30.0):
        self.__polling_thermal_time = polling_time
        self.__thermals = None
        self.__timer = None
        self.__chassis = None
        
    def start(self):
        self.work()
        self.__timer = Timer(self.__polling_thermal_time, self.start)
        self.__timer.start()

    def work(self):
        if self.__chassis is not None:
            self.__thermals = self.__chassis._thermal_list
            for term in self.__thermals:
                self.check(term)

    def check(self, sensor):
        temperature = sensor.get_temperature()
        if temperature is not None:
            temp_high = sensor.get_high_threshold()
            temp_low = sensor.get_low_threshold()
            if temp_high > -999.0:
                if temperature > temp_high:
                    print('Sensor ', sensor.get_name(), ' temperature more then', temp_high, '!!!')
            else:
                print('Sensor ', sensor.get_name(), ' has no high temperature threshold')

            if temp_low > -999.0:
                if temperature < temp_low:
                    print('Sensor ', sensor.get_name(), ' temperature less then', temp_low, '!!!')
            else:
                print('Sensor ', sensor.get_name(), ' has no low temperature threshold')
            
    def stop(self):
        if self.__timer is not None:
            self.__timer.cancel()

    def __del__(self):
        if self.__timer is not None:
            self.__timer.cancel()

    # for compatibility with old version
    def run_policy(self, chassis_def):
        self.__chassis = chassis_def

    def get_interval(self):
        return self.__polling_thermal_time

    def initialize(self):
        pass

    def load(self, json_file):
        pass

    def init_thermal_algorithm(self, chassis_def):
        self.__chassis = chassis_def
        self.start()

    def deinitialize(self):
        self.stop()

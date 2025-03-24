#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_thermal import PddfThermal
    from .helper import DeviceThreshold
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

NOT_AVAILABLE = DeviceThreshold.NOT_AVAILABLE
HIGH_THRESHOLD = DeviceThreshold.HIGH_THRESHOLD
LOW_THRESHOLD = DeviceThreshold.LOW_THRESHOLD
HIGH_CRIT_THRESHOLD = DeviceThreshold.HIGH_CRIT_THRESHOLD
LOW_CRIT_THRESHOLD = DeviceThreshold.LOW_CRIT_THRESHOLD

# Define keys as constants
MB_FRONT_MID = 'MB_FrontMiddle_temp(0x48)'
MB_RIGHT_CENTER = 'MB_RightCenter_temp(0x49)'
MB_LEFT_CENTER = 'MB_LeftCenter_temp(0x4a)'
CB_TEMP = 'CB_temp(0x4b)'
OCXO_TEMP = 'OCXO_temp(0x4c)'
FB1_TEMP = 'FB_1_temp(0x4e)'
FB2_TEMP = 'FB_2_temp(0x4f)'
CPU_PACKAGE = 'CPU_Package_temp'
CPU_CORE0 = 'CPU_Core_0_temp'
CPU_CORE1 = 'CPU_Core_1_temp'
CPU_CORE2 = 'CPU_Core_2_temp'
CPU_CORE3 = 'CPU_Core_3_temp'

DEFAULT_THRESHOLD = {
    MB_FRONT_MID : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    MB_RIGHT_CENTER : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    MB_LEFT_CENTER : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CB_TEMP  : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    OCXO_TEMP : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    FB1_TEMP : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    FB2_TEMP : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CPU_PACKAGE : {
        HIGH_THRESHOLD : '82.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : '104.0',
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CPU_CORE0 : {
        HIGH_THRESHOLD : '82.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : '104.0',
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CPU_CORE1 : {
        HIGH_THRESHOLD : '82.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : '104.0',
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CPU_CORE2 : {
        HIGH_THRESHOLD : '82.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : '104.0',
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    CPU_CORE3 : {
        HIGH_THRESHOLD : '82.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : '104.0',
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    'PSU-1 temp sensor 1' : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    },
    'PSU-2 temp sensor 1' : {
        HIGH_THRESHOLD : '80.0',
        LOW_THRESHOLD : NOT_AVAILABLE,
        HIGH_CRIT_THRESHOLD : NOT_AVAILABLE,
        LOW_CRIT_THRESHOLD : NOT_AVAILABLE
    }
}

class Thermal(PddfThermal):
    """PDDF Platform-Specific Thermal class"""

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None, is_psu_thermal=False, psu_index=0):
        PddfThermal.__init__(self, index, pddf_data, pddf_plugin_data, is_psu_thermal, psu_index)
        
        self.pddf_obj = pddf_data
        self.thermal_obj_name = "TEMP{}".format(self.thermal_index)
        self.thermal_obj = self.pddf_obj.data[self.thermal_obj_name]
        
        # Threshold Configuration
        self.__conf = DeviceThreshold(self.get_name())
        # Default threshold.
        self.__default_threshold = DEFAULT_THRESHOLD[self.get_name()]
        self.min_temperature = None
        self.max_temperature = None

    # Provide the functions/variables below for which implementation is to be overwritten
    def set_default_threshold(self, fan_dir):
        # The thermal policy configuration table is referenced from the accton_as9716_32d_monitor.py file
        # and is used for different fan directions (airflow modes).
        #
        # The table is organized by fan_dir values (0 and 1), where:
        # - fan_dir = 0: Front-to-back (F2B) airflow direction
        # - fan_dir = 1: Back-to-front (B2F) airflow direction
        #
        # Each sensor is mapped to a tuple (HIGH_THRESHOLD, HIGH_CRIT_THRESHOLD) representing:
        # - HIGH_THRESHOLD: The temperature at which a red alarm warning is triggered
        # - HIGH_CRIT_THRESHOLD: The temperature at which a system shutdown is triggered
        thermal_policy_config_table = {
            0: {
                MB_FRONT_MID: ('72.0', '78.0'),
                MB_RIGHT_CENTER: ('72.0', '78.0'),
                MB_LEFT_CENTER: ('72.0', '78.0'),
                CB_TEMP: ('60.0', '70.0'),
                OCXO_TEMP: ('72.0', '78.0'),
                FB1_TEMP: ('72.0', '78.0'),
                FB2_TEMP: ('72.0', '78.0'),
                CPU_PACKAGE: ('81.0', '87.0'),
                CPU_CORE0: ('81.0', '87.0'),
                CPU_CORE1: ('81.0', '87.0'),
                CPU_CORE2: ('81.0', '87.0'),
                CPU_CORE3: ('81.0', '87.0')
            },
            1: {
                MB_FRONT_MID: ('65.0', '71.0'),
                MB_RIGHT_CENTER: ('58.0', '64.0'),
                MB_LEFT_CENTER: ('57.0', '63.0'),
                CB_TEMP: ('50.0', '56.0'),
                OCXO_TEMP: ('57.0', '63.0'),
                FB1_TEMP: ('57.0', '63.0'),
                FB2_TEMP: ('60.0', '66.0'),
                CPU_PACKAGE: ('60.0', '66.0'),
                CPU_CORE0: ('60.0', '66.0'),
                CPU_CORE1: ('60.0', '66.0'),
                CPU_CORE2: ('60.0', '66.0'),
                CPU_CORE3: ('60.0', '66.0')
            }
        }
        for key, (ht, hct) in thermal_policy_config_table[fan_dir].items():
            if key == self.get_name():
                self.__default_threshold[HIGH_THRESHOLD] = ht
                self.__default_threshold[HIGH_CRIT_THRESHOLD] = hct

    def get_name(self):
        if self.is_psu_thermal:
            return "PSU-{0} temp sensor 1".format(self.thermals_psu_index)
        else:
            if 'dev_attr' in self.thermal_obj.keys():
                if 'display_name' in self.thermal_obj['dev_attr']:
                    return str(self.thermal_obj['dev_attr']['display_name'])

            # In case of errors
            return "Temp sensor {0}".format(self.thermal_index)

    def get_status(self):
        get_temp=self.get_temperature()

        if get_temp is not None:
            return True if get_temp else False

    def get_temperature(self):
        current = super().get_temperature()

        if self.min_temperature is None or \
            current < self.min_temperature:
            self.min_temperature = current

        if self.max_temperature is None or \
           current > self.max_temperature:
            self.max_temperature = current

        return current

    def set_high_threshold(self, temperature):
        try:
            value = float(temperature)
        except Exception:
            return False

        # The new value can not be more than the default value.
        default_value = self.__default_threshold[HIGH_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            if value > float(default_value):
                return False

        try:
            self.__conf.set_high_threshold(str(value))
        except Exception:
            return False

        return True

    def get_high_threshold(self):
        value = self.__conf.get_high_threshold()
        if value != NOT_AVAILABLE:
            return float(value)

        default_value = self.__default_threshold[HIGH_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            return float(default_value)
        
        return super().get_high_threshold()

    def set_low_threshold(self, temperature):
        try:
            value = float(temperature)
        except Exception:
            return False

        # The new value can not be less than the default value.
        default_value = self.__default_threshold[LOW_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            if value < float(default_value):
                return False

        try:
            self.__conf.set_low_threshold(str(value))
        except Exception:
            return False

        return True

    def get_low_threshold(self):
        value = self.__conf.get_low_threshold()
        if value != NOT_AVAILABLE:
            return float(value)

        default_value = self.__default_threshold[LOW_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            return float(default_value)

        raise NotImplementedError

    def set_high_critical_threshold(self, temperature):
        try:
            value = float(temperature)
        except Exception:
            return False

        # The new value can not be more than the default value.
        default_value = self.__default_threshold[HIGH_CRIT_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            if value > float(default_value):
                return False

        try:
            self.__conf.set_high_critical_threshold(str(value))
        except Exception:
            return False

        return True

    def get_high_critical_threshold(self):
        value = self.__conf.get_high_critical_threshold()
        if value != NOT_AVAILABLE:
            return float(value)

        default_value = self.__default_threshold[HIGH_CRIT_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            return float(default_value)
        return super().get_high_critical_threshold()

    def set_low_critical_threshold(self, temperature):
        try:
            value = float(temperature)
        except Exception:
            return False

        # The new value can not be less than the default value.
        default_value = self.__default_threshold[LOW_CRIT_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            if value < float(default_value):
                return False

        try:
            self.__conf.set_low_critical_threshold(str(value))
        except Exception:
            return False

        return True

    def get_low_critical_threshold(self):
        value = self.__conf.get_low_critical_threshold()
        if value != NOT_AVAILABLE:
            return float(value)

        default_value = self.__default_threshold[LOW_CRIT_THRESHOLD]
        if default_value != NOT_AVAILABLE:
            return float(default_value)

        raise NotImplementedError

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """
        return 'N/A'

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return 'N/A'

    def get_minimum_recorded(self):
        """
        Retrieves the minimum recorded temperature of thermal
        Returns:
            A float number, the minimum recorded temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.min_temperature is None:
            self.get_temperature()

        return self.min_temperature

    def get_maximum_recorded(self):
        """
        Retrieves the maximum recorded temperature of thermal
        Returns:
            A float number, the maximum recorded temperature of thermal in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        if self.max_temperature is None:
            self.get_temperature()

        return self.max_temperature

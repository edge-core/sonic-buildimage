#!/usr/bin/env python


try:
    from sonic_platform_pddf_base.pddf_fan import PddfFan
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")

FAN_NAME_LIST = ["FAN-1F", "FAN-1R", "FAN-2F", "FAN-2R",
                 "FAN-3F", "FAN-3R", "FAN-4F", "FAN-4R",
                 "FAN-5F", "FAN-5R"]

class Fan(PddfFan):
    """PDDF Platform-Specific Fan class"""

    def __init__(self, tray_idx, fan_idx=0, pddf_data=None, pddf_plugin_data=None, is_psu_fan=False, psu_index=0):
        # idx is 0-based 
        PddfFan.__init__(self, tray_idx, fan_idx, pddf_data, pddf_plugin_data, is_psu_fan, psu_index)

    # Provide the functions/variables below for which implementation is to be overwritten
    # Since psu_fan airflow direction cant be read from sysfs, it is fixed as 'F2B' or 'intake'

    def get_name(self):
        """
        Retrieves the name of the device
            Returns:
            string: The name of the device
        """
        fan_name = FAN_NAME_LIST[(self.fantray_index-1)*2 + self.fan_index-1] \
            if not self.is_psu_fan \
            else "PSU-{} FAN-{}".format(self.fans_psu_index, self.fan_index)

        return fan_name

    def get_direction(self):
        """
        Retrieves the direction of fan

        Returns:
            A string, either FAN_DIRECTION_INTAKE or FAN_DIRECTION_EXHAUST
            depending on fan direction
        """
        if self.is_psu_fan:
            direction = self.FAN_DIRECTION_INTAKE

        else:
            idx = (self.fantray_index-1)*self.platform['num_fans_pertray'] + self.fan_index
            attr = "fan" + str(idx) + "_direction"
            output = self.pddf_obj.get_attr_name_output("FAN-CTRL", attr)
            if not output:
                return False

            mode = output['mode']
            val = output['status']

            val = val.rstrip()
            vmap = self.plugin_data['FAN']['direction'][mode]['valmap']
            if val in vmap:
                direction = vmap[val]
            else:
                direction = val

        return direction

    def get_model(self):
        """
        Retrieves the model number (or part number) of the device
        Returns:
            string: Model/part number of device
        """

        return "N/A"

    def get_serial(self):
        """
        Retrieves the serial number of the device
        Returns:
            string: Serial number of device
        """
        return "N/A"

    def get_target_speed(self):
        """
        Retrieves the target (expected) speed of the fan

        Returns:
            An integer, the percentage of full fan speed, in the range 0 (off)
                 to 100 (full speed)
        """
        if self.is_psu_fan:
            return super().get_speed()
        else:
            return super().get_target_speed()

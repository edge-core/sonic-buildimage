#!/usr/bin/env python
#


try:
    from sonic_platform_pddf_base.pddf_psu import PddfPsu
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


class Psu(PddfPsu):
    """PDDF Platform-Specific PSU class"""
    

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfPsu.__init__(self, index, pddf_data, pddf_plugin_data)
        
    # Provide the functions/variables below for which implementation is to be overwritten
    def get_name(self):
        return "PSU-{}".format(self.psu_index)

    def get_revision(self):
        """
        Retrieves the hardware revision of the device

        Returns:
            string: Revision value of device
        """
        return 'N/A'

    def get_temperature_high_threshold(self):
        """
        Retrieves the high threshold temperature of PSU
        Returns:
            A float number, the high threshold temperature of PSU in Celsius
            up to nearest thousandth of one degree Celsius, e.g. 30.125
        """
        threshold = super().get_temperature_high_threshold()

        for psu_thermal_idx in range(self.num_psu_thermals):
            try:
                tmp = self._thermal_list[psu_thermal_idx].get_high_threshold()
                if threshold > tmp or threshold == 0.0:
                    threshold = tmp
            except Exception:
                pass

        return threshold

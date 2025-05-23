#!/usr/bin/env python

try:
    from sonic_platform_pddf_base.pddf_sfp import PddfSfp
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")


class Sfp(PddfSfp):
    """
    PDDF Platform-Specific Sfp class
    """

    def __init__(self, index, pddf_data=None, pddf_plugin_data=None):
        PddfSfp.__init__(self, index, pddf_data, pddf_plugin_data)

    # Provide the functions/variables below for which implementation is to be overwritten
    def get_position_in_parent(self):
        """Retrieves 1-based relative physical position in parent device."""
        return self.port_index

    def get_lpmode(self):

        lpmode = False

        if self.get_presence()==False:
            return False

        device = 'PORT{}'.format(self.port_index)
        output = self.pddf_obj.get_attr_name_output(device, 'xcvr_lpmode')

        if output:
            status = int(output['status'].rstrip())

            if status == 1:
                lpmode = True
            else:
                lpmode = False
        else:
            xcvr_id = self._xcvr_api_factory._get_id()

            if xcvr_id is not None:
                if xcvr_id == 0x18 or xcvr_id == 0x19 or xcvr_id == 0x1e:
                    # QSFP-DD or OSFP
                    # Use common SfpOptoeBase implementation for get_lpmode
                    lpmode = super().get_lpmode()
                elif xcvr_id == 0x11 or xcvr_id == 0x0d or xcvr_id == 0x0c:
                    # QSFP28, QSFP+, QSFP
                    # get_power_set() is not defined in the optoe_base class
                    api = self.get_xcvr_api()
                    power_set = api.get_power_set()
                    power_override = self.get_power_override()
                    
                    return power_set if power_override else False

        return lpmode
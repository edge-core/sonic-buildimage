#!/usr/bin/env python

#############################################################################
# PDDF
# Module contains an implementation of SONiC Chassis API
#
#############################################################################

try:
    import time
    from sonic_platform_pddf_base.pddf_chassis import PddfChassis
except ImportError as e:
    raise ImportError(str(e) + "- required module not found")


class Chassis(PddfChassis):
    """
    PDDF Platform-specific Chassis class
    """

    def __init__(self, pddf_data=None, pddf_plugin_data=None):
        PddfChassis.__init__(self, pddf_data, pddf_plugin_data)

    # Provide the functions/variables below for which implementation is to be overwritten
    sfp_change_event_data = {'valid': 0, 'last': 0, 'present': 0}
    def get_change_event(self, timeout=2000):
        now = time.time()
        port_dict = {}
        change_dict = {}
        change_dict['sfp'] = port_dict

        if timeout < 1000:
            timeout = 1000
        timeout = timeout / float(1000)  # Convert to secs

        if now < (self.sfp_change_event_data['last'] + timeout) and self.sfp_change_event_data['valid']:
            return True, change_dict
        
        bitmap = 0
        for i in range(34):
            modpres = self.get_sfp(i).get_presence()
            if modpres:
                bitmap = bitmap | (1 << i)

        changed_ports = self.sfp_change_event_data['present'] ^ bitmap
        if changed_ports:
            for i in range(34):
                if (changed_ports & (1 << i)):
                    if (bitmap & (1 << i)) == 0:
                        port_dict[i+1] = '0'
                    else:
                        port_dict[i+1] = '1'


            # Update teh cache dict
            self.sfp_change_event_data['present'] = bitmap
            self.sfp_change_event_data['last'] = now
            self.sfp_change_event_data['valid'] = 1
            return True, change_dict
        else:
            return True, change_dict

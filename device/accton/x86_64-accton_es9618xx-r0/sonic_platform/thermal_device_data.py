DEVICE_DATA = {
    'thermal': {
        'thresholds': {
            # Dictionary mapping temperature sensor names to lists of thresholds
            # and cooling levels, where each list element follows this format:
            # "thermal low threshold : thermal high threshold : fan cooling level"
            'thermal_x48'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'thermal_x49'   : ["62:66:10", "67:71:10",  "76:81:10"],
            'thermal_x4A'   : ["55:59:10", "60:64:10",  "78:84:10"],
            'thermal_x4B'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'thermal_x4C'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'thermal_x4D'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'thermal_x4E'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'thermal_x4F'   : ["64:69:10", "70:75:10",  "80:85:10"],
            'asic_diode'    : ["70:90:10", "98:105:10", "109:115:10"],
            'asic_sensor_1' : ["70:90:10", "98:105:10", "109:115:10"],
            'asic_sensor_2' : ["70:90:10", "98:105:10", "109:115:10"],
            'asic_sensor_3' : ["70:90:10", "98:105:10", "109:115:10"],
            'asic_average'  : ["70:90:10", "98:105:10", "109:115:10"],
            'asic_maximum'  : ["70:90:10", "98:105:10", "109:115:10"]
        }
    }
}


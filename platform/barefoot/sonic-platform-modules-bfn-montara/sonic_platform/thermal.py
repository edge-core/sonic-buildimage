try:
    import subprocess

    from sonic_platform.bfn_extensions.platform_sensors import platform_sensors_get
    from sonic_platform_base.thermal_base import ThermalBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

'''
data argument is in "sensors -A -u" format, example:
coretemp-isa-0000
Package id 0:
  temp1_input: 37.000
  temp1_max: 82.000
  temp1_crit: 104.000
  temp1_crit_alarm: 0.000
Core 0:
  temp2_input: 37.000
  ...
'''
def _sensors_chip_parsed(data: str):
    def kv(line):
        k, v, *_ = [t.strip(': ') for t in line.split(':') if t] + ['']
        return k, v

    chip, *data = data.strip().split('\n')
    chip = chip.strip(': ')

    sensors = []
    for line in data:
        if not line.startswith(' '):
            sensor_label = line.strip(': ')
            sensors.append((sensor_label, {}))
            continue

        if len(sensors) == 0:
            raise RuntimeError(f'invalid data to parse: {data}')

        attr, value = kv(line)
        sensor_label, sensor_data = sensors[-1]
        sensor_data.update({attr: value})

    return chip, dict(sensors)

'''
Example of returned dict:
{
    'coretemp-isa-0000': {
        'Core 1': { "temp1_input": 40, ...  },
        'Core 2': { ... }
    }
}
'''
def _sensors_get() -> dict:
    data = platform_sensors_get(['-A', '-u']) or ''
    data += subprocess.check_output("/usr/bin/sensors -A -u",
                shell=True, text=True)
    data = data.split('\n\n')
    data = [_sensors_chip_parsed(chip_data) for chip_data in data if chip_data]
    data = dict(data)
    return data

def _value_get(d: dict, key_prefix, key_suffix=''):
    for k, v in d.items():
        if k.startswith(key_prefix) and k.endswith(key_suffix):
            return v
    return None

# Thermal -> ThermalBase -> DeviceBase
class Thermal(ThermalBase):
    def __init__(self, chip, label):
        self.__chip = chip
        self.__label = label
        self.__name = f"{chip}:{label}".lower().replace(' ', '-')

    def __get(self, attr_prefix, attr_suffix):
        sensor_data = _sensors_get().get(self.__chip, {}).get(self.__label, {})
        value = _value_get(sensor_data, attr_prefix, attr_suffix)
        if value is not None: return value
        raise NotImplementedError

    # ThermalBase interface methods:
    def get_temperature(self) -> float:
        return float(self.__get('temp', 'input'))

    def get_high_threshold(self) -> float:
        return float(self.__get('temp', 'max'))

    def get_high_critical_threshold(self) -> float:
        return float(self.__get('temp', 'crit'))

    # DeviceBase interface methods:
    def get_name(self):
        return self.__name

    def get_presence(self):
        return True

    def get_status(self):
        return True

def thermal_list_get():
    l = []
    for chip, chip_data in _sensors_get().items():
        for sensor, sensor_data in chip_data.items():
            # add only temperature sensors
            if _value_get(sensor_data, "temp") is not None:
                l.append(Thermal(chip, sensor))
    return l

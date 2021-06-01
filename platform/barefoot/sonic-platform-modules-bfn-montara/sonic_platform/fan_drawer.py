try:
    from sonic_platform.platform_thrift_client import thrift_try
    from sonic_platform_base.fan_drawer_base import FanDrawerBase
    from sonic_platform_base.fan_base import FanBase
except ImportError as e:
    raise ImportError (str(e) + "- required module not found")

_MAX_FAN = 10

def _fan_info_get(fan_num, cb, default=None):
    def get_data(client):
        return client.pltfm_mgr.pltfm_mgr_fan_info_get(fan_num)
    fan_info = thrift_try(get_data)
    if fan_num == fan_info.fan_num:
        return cb(fan_info)
    if default is None:
        raise LookupError
    return default

def _fan_info_get_all():
    for fan_num in range(1, _MAX_FAN + 1):
        def get_data(client, fan_num=fan_num):
            return client.pltfm_mgr.pltfm_mgr_fan_info_get(fan_num)
        fan_info = thrift_try(get_data)
        if fan_info.fan_num == fan_num:
            yield fan_info

# Fan -> FanBase -> DeviceBase
class Fan(FanBase):
    def __init__(self, num):
        self.__num = num

    # FanBase interface methods:
    # returns speed in percents
    def get_speed(self):
        def cb(info): return info.percent
        return _fan_info_get(self.__num, cb, 0)

    def set_speed(self, percent):
        def set_fan_speed(client):
            return client.pltfm_mgr.pltfm_mgr_fan_speed_set(self.__num, percent)
        return thrift_try(set_fan_speed)

    # DeviceBase interface methods:
    def get_name(self):
        return f"counter-rotating-fan-{self.__num}"

    def get_presence(self):
        return _fan_info_get(self.__num, lambda _: True, False)

    def get_position_in_parent(self):
        return self.__num

    def is_replaceable(self):
        return True

    def get_status(self):
        return True

# FanDrawer -> FanDrawerBase -> DeviceBase
class FanDrawer(FanDrawerBase):
    def __init__(self):
        # For now we return only present fans
        self._fan_list = [Fan(i.fan_num) for i in _fan_info_get_all()]

    # DeviceBase interface methods:
    def get_name(self):
        return 'fantray'

    def get_presence(self):
        return True

    def get_status(self):
        return True

def fan_drawer_list_get():
    return [FanDrawer()]

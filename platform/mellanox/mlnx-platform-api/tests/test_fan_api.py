import os
import sys
from mock import MagicMock

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

from sonic_platform.fan import Fan


def test_get_absence_fan_direction():
    fan = Fan(True, 0, 0)
    fan.get_presence = MagicMock(return_value=False)
    assert fan.fan_dir is not None
    assert not fan.is_psu_fan
    assert fan.get_direction() == Fan.FAN_DIRECTION_NOT_APPLICABLE

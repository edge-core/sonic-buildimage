# system health python2 wheel

SYSTEM_HEALTH = system_health-1.0-py2-none-any.whl
$(SYSTEM_HEALTH)_SRC_PATH = $(SRC_PATH)/system-health
$(SYSTEM_HEALTH)_PYTHON_VERSION = 2
$(SYSTEM_HEALTH)_DEPENDS = $(SONIC_PY_COMMON_PY2) $(SWSSSDK_PY2) $(SONIC_CONFIG_ENGINE)
SONIC_PYTHON_WHEELS += $(SYSTEM_HEALTH)

export system_health_py2_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SYSTEM_HEALTH))"

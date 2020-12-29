# system health Python wheel

SYSTEM_HEALTH = system_health-1.0-py3-none-any.whl
$(SYSTEM_HEALTH)_SRC_PATH = $(SRC_PATH)/system-health
$(SYSTEM_HEALTH)_PYTHON_VERSION = 3
$(SYSTEM_HEALTH)_DEPENDS = $(SONIC_PY_COMMON_PY3) $(SWSSSDK_PY3) $(SONIC_CONFIG_ENGINE_PY3)
SONIC_PYTHON_WHEELS += $(SYSTEM_HEALTH)

export system_health_py3_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SYSTEM_HEALTH))"

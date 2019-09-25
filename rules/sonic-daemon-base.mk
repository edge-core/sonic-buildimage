# SONIC_DAEMON_BASE_PY2 package

SONIC_DAEMON_BASE_PY2 = sonic_daemon_base-1.0-py2-none-any.whl
$(SONIC_DAEMON_BASE_PY2)_SRC_PATH = $(SRC_PATH)/sonic-daemon-base
$(SONIC_DAEMON_BASE_PY2)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_DAEMON_BASE_PY2)

export daemon_base_py2_wheel_path="$(addprefix $(PYTHON_WHEELS_PATH)/,$(SONIC_DAEMON_BASE_PY2))"

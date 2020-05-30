# swsssdk python3 wheel

SWSSSDK_PY3 = swsssdk-2.0.1-py3-none-any.whl
$(SWSSSDK_PY3)_SRC_PATH = $(SRC_PATH)/sonic-py-swsssdk
$(SWSSSDK_PY3)_PYTHON_VERSION = 3
# Synthetic dependency just to avoid race condition
$(SWSSSDK_PY3)_DEPENDS += $(SWSSSDK_PY2) $(REDIS_DUMP_LOAD_PY3)
SONIC_PYTHON_WHEELS += $(SWSSSDK_PY3)

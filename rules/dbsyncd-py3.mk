# sonic-dbsyncd python3 wheel

DBSYNCD_PY3 = sonic_d-2.0.0-py3-none-any.whl
$(DBSYNCD_PY3)_SRC_PATH = $(SRC_PATH)/sonic-dbsyncd
$(DBSYNCD_PY3)_PYTHON_VERSION = 3
$(DBSYNCD_PY3)_DEPENDS += $(SWSSSDK_PY3)
SONIC_PYTHON_WHEELS += $(DBSYNCD_PY3)

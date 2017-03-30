# sonic-dbsyncd python2 wheel

DBSYNCD_PY2 = sonic_d-2.0.0-py2-none-any.whl
$(DBSYNCD_PY2)_SRC_PATH = $(SRC_PATH)/sonic-dbsyncd
$(DBSYNCD_PY2)_PYTHON_VERSION = 2
$(DBSYNCD_PY2)_DEPENDS += $(SWSSSDK_PY2)
SONIC_PYTHON_WHEELS += $(DBSYNCD_PY2)

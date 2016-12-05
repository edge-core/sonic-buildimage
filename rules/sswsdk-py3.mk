# sswsdk python3 wheel

SSWSDK_PY3 = sswsdk-2.0.1-py3-none-any.whl
$(SSWSDK_PY3)_SRC_PATH = $(SRC_PATH)/sonic-py-swsssdk
$(SSWSDK_PY3)_PYTHON_VERSION = 3
# Synthetic dependency just to avoid race condition
$(SSWSDK_PY3)_DEPENDS += $(SSWSDK_PY2)
SONIC_PYTHON_WHEELS += $(SSWSDK_PY3)

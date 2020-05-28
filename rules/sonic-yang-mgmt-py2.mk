# sonic-yang-mgmt python2 wheel

SONIC_YANG_MGMT_PY = sonic_yang_mgmt-1.0-py2-none-any.whl
$(SONIC_YANG_MGMT_PY)_SRC_PATH = $(SRC_PATH)/sonic-yang-mgmt
$(SONIC_YANG_MGMT_PY)_PYTHON_VERSION = 2
$(SONIC_YANG_MGMT_PY)_DEBS_DEPENDS = $(LIBYANG) $(LIBYANG_CPP) $(LIBYANG_PY2) \
                                     $(LIBYANG_PY3)
$(SONIC_YANG_MGMT_PY)_DEPENDS =  $(SONIC_YANG_MODELS_PY3)
$(SONIC_YANG_MGMT_PY)_RDEPENDS = $(SONIC_YANG_MODELS_PY3) $(LIBYANG) \
                                 $(LIBYANG_CPP) $(LIBYANG_PY2)

SONIC_PYTHON_WHEELS += $(SONIC_YANG_MGMT_PY)

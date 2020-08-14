# sonic-psud (SONiC PSU daemon) Debian package

SONIC_PSUD = sonic_psud-1.0-py2-none-any.whl
$(SONIC_PSUD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-psud
$(SONIC_PSUD)_DEPENDS = $(SONIC_PY_COMMON_PY2)
$(SONIC_PSUD)_PYTHON_VERSION = 2
SONIC_PYTHON_WHEELS += $(SONIC_PSUD)

# sonic-psud (SONiC PSU daemon) Debian package

SONIC_PSUD = python-sonic-psud_1.0-1_all.deb
$(SONIC_PSUD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-psud
$(SONIC_PSUD)_WHEEL_DEPENDS = $(SONIC_PY_COMMON_PY2)
SONIC_PYTHON_STDEB_DEBS += $(SONIC_PSUD)

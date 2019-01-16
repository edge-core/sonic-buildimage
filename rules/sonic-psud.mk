# sonic-psud (SONiC PSU daemon) Debian package

SONIC_PSUD = python-sonic-psud_1.0-1_all.deb
$(SONIC_PSUD)_SRC_PATH = $(SRC_PATH)/sonic-platform-daemons/sonic-psud
SONIC_PYTHON_STDEB_DEBS += $(SONIC_PSUD)

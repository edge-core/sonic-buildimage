# monit package

MONIT_VERSION = 5.20.0-6

export MONIT_VERSION

MONIT = monit_$(MONIT_VERSION)_amd64.deb
$(MONIT)_SRC_PATH = $(SRC_PATH)/monit
SONIC_MAKE_DEBS += $(MONIT)

SONIC_STRETCH_DEBS += $(MONIT)

MONIT_DBG = monit-dbgsym_$(MONIT_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(MONIT),$(MONIT_DBG)))

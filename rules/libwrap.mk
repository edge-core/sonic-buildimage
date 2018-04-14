# libwrap packages

LIBWRAP_VERSION = 7.6.q-25

export LIBWRAP_VERSION

LIBWRAP = libwrap0_$(LIBWRAP_VERSION)_amd64.deb
$(LIBWRAP)_SRC_PATH = $(SRC_PATH)/libwrap
SONIC_MAKE_DEBS += $(LIBWRAP)

TCPD = tcpd_$(LIBWRAP_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(LIBWRAP),$(TCPD)))

# libhiredis package

HIREDIS_VERSION = 0.14.0
HIREDIS_VERSION_FULL = $(HIREDIS_VERSION)-3~bpo9+1

export HIREDIS_VERSION HIREDIS_VERSION_FULL

LIBHIREDIS = libhiredis0.14_$(HIREDIS_VERSION_FULL)_amd64.deb
$(LIBHIREDIS)_SRC_PATH = $(SRC_PATH)/hiredis
SONIC_MAKE_DEBS += $(LIBHIREDIS)

LIBHIREDIS_DEV = libhiredis-dev_$(HIREDIS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LIBHIREDIS),$(LIBHIREDIS_DEV)))

LIBHIREDIS_DBG = libhiredis0.14-dbgsym_$(HIREDIS_VERSION_FULL)_amd64.deb
$(eval $(call add_derived_package,$(LIBHIREDIS),$(LIBHIREDIS_DBG)))

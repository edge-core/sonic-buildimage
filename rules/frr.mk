# FRRouting (frr) package

FRR_VERSION = 4.0
export FRR_VERSION

FRR = frr_$(FRR_VERSION)-1~sonic.debian8+1_amd64.deb
$(FRR)_DEPENDS += $(LIBSNMP_DEV)
$(FRR)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR)

FRR_DBG = frr-dbgsym_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_amd64.deb
$(eval $(call add_derived_package,$(FRR),$(FRR_DBG)))

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += sonic-frr


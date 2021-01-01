# FRRouting (frr) package

FRR_VERSION = 7.5
FRR_SUBVERSION = 0
FRR_BRANCH = frr/7.5
FRR_TAG = frr-7.5-s1
export FRR_VERSION FRR_SUBVERSION FRR_BRANCH FRR_TAG


FRR = frr_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_$(CONFIGURED_ARCH).deb
$(FRR)_DEPENDS += $(LIBSNMP_DEV) $(LIBYANG1) $(LIBYANG1_DEV)
$(FRR)_RDEPENDS += $(LIBYANG1)
$(FRR)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR)

FRR_PYTHONTOOLS = frr-pythontools_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_all.deb
$(eval $(call add_extra_package,$(FRR),$(FRR_PYTHONTOOLS)))

FRR_DBG = frr-dbgsym_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(FRR),$(FRR_DBG)))

FRR_SNMP = frr-snmp_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_$(CONFIGURED_ARCH).deb
$(eval $(call add_extra_package,$(FRR),$(FRR_SNMP)))

FRR_SNMP_DBG = frr-snmp-dbgsym_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_$(CONFIGURED_ARCH).deb
$(eval $(call add_derived_package,$(FRR),$(FRR_SNMP_DBG)))

export FRR FRR_PYTHONTOOLS FRR_DBG FRR_SNMP FRR_SNMP_DBG

# The .c, .cpp, .h & .hpp files under src/{$DBG_SRC_ARCHIVE list}
# are archived into debug one image to facilitate debugging.
#
DBG_SRC_ARCHIVE += sonic-frr

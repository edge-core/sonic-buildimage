# FRRouting (frr) package

FRR_VERSION = 7.0.1
FRR_SUBVERSION = 0
export FRR_VERSION FRR_SUBVERSION


FRR = frr_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_amd64.deb
$(FRR)_DEPENDS += $(LIBSNMP_DEV) $(LIBYANG_DEV)
$(FRR)_RDEPENDS += $(LIBYANG)
$(FRR)_SRC_PATH = $(SRC_PATH)/sonic-frr
SONIC_MAKE_DEBS += $(FRR)
SONIC_STRETCH_DEBS += $(FRR)

FRR_PYTHONTOOLS = frr-pythontools_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_all.deb
$(eval $(call add_derived_package,$(FRR),$(FRR_PYTHONTOOLS)))

FRR_DBG = frr-dbgsym_$(FRR_VERSION)-sonic-$(FRR_SUBVERSION)_amd64.deb
$(eval $(call add_derived_package,$(FRR),$(FRR_DBG)))

export FRR FRR_PYTHONTOOLS FRR_DBG

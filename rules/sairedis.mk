# sairedis package

LIBSAIREDIS = libsairedis_1.0.0_amd64.deb
$(LIBSAIREDIS)_SRC_PATH = $(SRC_PATH)/sonic-sairedis
$(LIBSAIREDIS)_DEPENDS += $(LIBSWSSCOMMON_DEV) $(LIBTHRIFT_DEV)
$(LIBSAIREDIS)_RDEPENDS += $(LIBSWSSCOMMON)
$(LIBSAIREDIS)_DEB_BUILD_OPTIONS = nocheck
SONIC_DPKG_DEBS += $(LIBSAIREDIS)

LIBSAIREDIS_DEV = libsairedis-dev_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIREDIS_DEV)))

LIBSAIVS = libsaivs_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIVS)))

LIBSAIVS_DEV = libsaivs-dev_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIVS_DEV)))

ifneq ($(CONFIGURED_PLATFORM),vs)
SYNCD = syncd_1.0.0_amd64.deb
$(SYNCD)_RDEPENDS += $(LIBSAIREDIS) $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD)))

SYNCD_RPC = syncd-rpc_1.0.0_amd64.deb
$(SYNCD_RPC)_RDEPENDS += $(LIBSAIREDIS) $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD_RPC)))
endif

LIBSAIMETADATA = libsaimetadata_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIMETADATA)))

LIBSAIMETADATA_DEV = libsaimetadata-dev_1.0.0_amd64.deb
$(LIBSAIMETADATA_DEV)_DEPENDS += $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIMETADATA_DEV)))

LIBSAIREDIS_DBG = libsairedis-dbg_1.0.0_amd64.deb
$(LIBSAIREDIS_DBG)_DEPENDS += $(LIBSAIREDIS)
$(LIBSAIREDIS_DBG)_RDEPENDS += $(LIBSAIREDIS)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIREDIS_DBG)))

LIBSAIVS_DBG = libsaivs-dbg_1.0.0_amd64.deb
$(LIBSAIVS_DBG)_DEPENDS += $(LIBSAIVS)
$(LIBSAIVS_DBG)_RDEPENDS += $(LIBSAIVS)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIVS_DBG)))

ifneq ($(CONFIGURED_PLATFORM),vs)
SYNCD_DBG = syncd-dbg_1.0.0_amd64.deb
$(SYNCD_DBG)_DEPENDS += $(SYNCD)
$(SYNCD_DBG)_RDEPENDS += $(SYNCD)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD_DBG)))

SYNCD_RPC_DBG = syncd-rpc-dbg_1.0.0_amd64.deb
$(SYNCD_RPC_DBG)_DEPENDS += $(SYNCD_RPC)
$(SYNCD_RPC_DBG)_RDEPENDS += $(SYNCD_RPC)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD_RPC_DBG)))
endif

LIBSAIMETADATA_DBG = libsaimetadata-dbg_1.0.0_amd64.deb
$(LIBSAIMETADATA_DBG)_DEPENDS += $(LIBSAIMETADATA)
$(LIBSAIMETADATA_DBG)_RDEPENDS += $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIMETADATA_DBG)))

# sairedis package

LIBSAIREDIS = libsairedis_1.0.0_amd64.deb
$(LIBSAIREDIS)_SRC_PATH = $(SRC_PATH)/sonic-sairedis
$(LIBSAIREDIS)_DEPENDS += $(LIBSWSSCOMMON_DEV) $(LIBTHRIFT_DEV)
$(LIBSAIREDIS)_RDEPENDS += $(LIBSWSSCOMMON)
SONIC_DPKG_DEBS += $(LIBSAIREDIS)

LIBSAIREDIS_DEV = libsairedis-dev_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIREDIS_DEV)))

SYNCD = syncd_1.0.0_amd64.deb
$(SYNCD)_RDEPENDS += $(LIBSAIREDIS) $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD)))

SYNCD_RPC = syncd-rpc_1.0.0_amd64.deb
$(SYNCD_RPC)_RDEPENDS += $(LIBSAIREDIS) $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(SYNCD_RPC)))

LIBSAIMETADATA = libsaimetadata_1.0.0_amd64.deb
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIMETADATA)))

LIBSAIMETADATA_DEV = libsaimetadata-dev_1.0.0_amd64.deb
$(LIBSAIMETADATA_DEV)_DEPENDS += $(LIBSAIMETADATA)
$(eval $(call add_derived_package,$(LIBSAIREDIS),$(LIBSAIMETADATA_DEV)))

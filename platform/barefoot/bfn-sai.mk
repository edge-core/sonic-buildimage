BFN_SAI = bfnsdk_20210324_deb10.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/dev/$(BFN_SAI)"

$(BFN_SAI)_DEPENDS += $(LIBNL_GENL3_DEV)
$(eval $(call add_conflict_package,$(BFN_SAI),$(LIBSAIVS_DEV)))
$(BFN_SAI)_RDEPENDS += $(LIBNL_GENL3)

SONIC_ONLINE_DEBS += $(BFN_SAI)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

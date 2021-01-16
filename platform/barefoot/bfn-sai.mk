BFN_SAI = bfnsdk_8.5.x.59217b4.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_8_5/bfnsdk_8.5.x.59217b4.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)
$(BFN_SAI_DEV)_CONFLICTS += $(LIBSAIVS_DEV)

BFN_SAI = bfnsdk_8_9_1.x.ab1e16f.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_8_9_1/bfnsdk_8_9_1.x.ab1e16f.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

BFN_SAI = bfnsdk_9.1.0.fddc672_deb9.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_9_1/bfnsdk_9.1.0.fddc672_deb9.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

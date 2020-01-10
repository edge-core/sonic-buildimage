BFN_SAI = bfnsdk_20191227_deb9.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/dev/bfnsdk_20191227_deb9.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

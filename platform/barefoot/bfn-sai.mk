BFN_SAI = bfnsdk_1.0.0_amd64.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/sde-sai1.3.3/bfnsdk_1.0.0_amd64.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

BFN_SAI = bfnsdk_master.df38274.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/vxlan_poc/bfnsdk_master.df38274.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

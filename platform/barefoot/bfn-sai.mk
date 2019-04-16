ifdef BLDENV
BFN_SAI = bfnsdk_master.92171a1_deb9.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/sde-master/bfnsdk_master.92171a1_deb9.deb"
else
BFN_SAI = bfnsdk_master.92171a1_deb8.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/sde-master/bfnsdk_master.92171a1_deb8.deb"
endif

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

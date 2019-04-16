ifdef BLDENV
BFN_PLATFORM = bfnplatform_master.92171a1_deb9.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/sde-master/bfnplatform_master.92171a1_deb9.deb"
else
BFN_PLATFORM = bfnplatform_master.92171a1_deb8.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/sde-master/bfnplatform_master.92171a1_deb8.deb"
endif

SONIC_ONLINE_DEBS += $(BFN_PLATFORM) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

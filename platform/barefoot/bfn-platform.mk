BFN_PLATFORM = bfnplatform_20210405_sai_1.5.2_deb9.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/dev/$(BFN_PLATFORM)"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

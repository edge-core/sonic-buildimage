BFN_PLATFORM = bfnplatform_20191227_deb9.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/dev/bfnplatform_20191227_deb9.deb"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

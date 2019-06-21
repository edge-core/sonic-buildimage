BFN_PLATFORM = bfnplatform_8_9_1.x.ab1e16f.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_8_9_1/bfnplatform_8_9_1.x.ab1e16f.deb"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

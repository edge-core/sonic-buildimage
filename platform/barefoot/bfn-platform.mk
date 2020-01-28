BFN_PLATFORM = bfnplatform_9.1.0.fddc672_deb9.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_9_1/$(BFN_PLATFORM)"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

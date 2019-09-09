BFN_PLATFORM = bfnplatform_9.0.0.cc6ccbe_pr_deb9.deb
$(BFN_PLATFORM)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_9_0/bfnplatform_9.0.0.cc6ccbe_pr_deb9.deb"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

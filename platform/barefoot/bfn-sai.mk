BFN_SAI = bfnsdk_9.0.0.cc6ccbe_pr_deb9.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_9_0/bfnsdk_9.0.0.cc6ccbe_pr_deb9.deb"

SONIC_ONLINE_DEBS += $(BFN_SAI)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

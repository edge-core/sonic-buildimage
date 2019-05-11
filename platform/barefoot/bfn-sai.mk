ifdef BLDENV
BFN_SAI = bfnsdk_8.9.x.98de3ce_pr_deb9.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_8_9/bfnsdk_8.9.x.98de3ce_pr_deb9.deb"
else
BFN_SAI = bfnsdk_8.9.x.98de3ce_pr_deb8.deb
$(BFN_SAI)_URL = "https://github.com/barefootnetworks/sonic-release-pkgs/raw/rel_8_9/bfnsdk_8.9.x.98de3ce_pr_deb8.deb"
endif

SONIC_ONLINE_DEBS += $(BFN_SAI) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_SAI)

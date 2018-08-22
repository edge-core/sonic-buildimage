BFN_PLATFORM = bfnplatform_1.0.0_amd64.deb
$(BFN_PLATFORM)_URL =	"https://github.com/barefootnetworks/sonic-release-pkgs/raw/201807/bfnplatform_1.0.0_amd64.deb"

SONIC_ONLINE_DEBS += $(BFN_PLATFORM) # $(BFN_SAI_DEV)
$(BFN_SAI_DEV)_DEPENDS += $(BFN_PLATFORM)

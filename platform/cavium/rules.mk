CAVM_LIBSAI = libsai.deb
$(CAVM_LIBSAI)_PATH = $(PLATFORM_PATH)/cavm_sdk
CAVM_SAI = sai.deb
$(CAVM_SAI)_PATH = $(PLATFORM_PATH)/cavm_sdk
XP_TOOLS = xp-tools.deb
$(XP_TOOLS)_PATH = $(PLATFORM_PATH)/cavm_sdk
XPSHELL = xpshell.deb
$(XPSHELL)_PATH = $(PLATFORM_PATH)/cavm_sdk

SONIC_COPY_DEBS += $(CAVM_LIBSAI) $(CAVM_SAI) $(XP_TOOLS) $(XPSHELL)

# TODO: Put dependencies for SDK packages

SONIC_ALL += $(SONIC_GENERIC) $(DOCKER_SYNCD_CAVM) $(DOCKER_ORCHAGENT) \
	     $(DOCKER_FPM)

# Inject cavm sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(CAVM_LIBSAI)

# Runtime dependency on cavm sai is set only for syncd
$(SYNCD)_RDEPENDS += $(CAVM_LIBSAI)

# Cavium SAI

CAVM_LIBSAI = libsai.deb
$(CAVM_LIBSAI)_PATH = $(PLATFORM_PATH)/cavm_sdk
CAVM_SAI = sai.deb
$(CAVM_SAI)_PATH = $(PLATFORM_PATH)/cavm_sdk
XP_TOOLS = xp-tools.deb
$(XP_TOOLS)_PATH = $(PLATFORM_PATH)/cavm_sdk
XPSHELL = xpshell.deb
$(XPSHELL)_PATH = $(PLATFORM_PATH)/cavm_sdk

SONIC_COPY_DEBS += $(CAVM_LIBSAI) $(CAVM_SAI) $(XP_TOOLS) $(XPSHELL)

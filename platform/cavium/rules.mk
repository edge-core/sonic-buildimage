include $(PLATFORM_PATH)/cavm-sai.mk
include $(PLATFORM_PATH)/docker-syncd-cavm.mk
include $(PLATFORM_PATH)/docker-orchagent-cavm.mk
include $(PLATFORM_PATH)/cavm_platform_modules.mk
include $(PLATFORM_PATH)/single-image.mk

SONIC_ALL += $(SONIC_SINGLE_IMAGE)

# Inject cavium sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(CAVM_SAI) $(CAVM_LIBSAI)

# Runtime dependency on cavium sai is set only for syncd
$(SYNCD)_RDEPENDS += $(CAVM_SAI)


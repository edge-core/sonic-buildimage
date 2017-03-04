include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/docker-orchagent-centec.mk
include $(PLATFORM_PATH)/docker-syncd-centec.mk
include $(PLATFORM_PATH)/one-image.mk

SONIC_ALL += $(SONIC_ONE_IMAGE)

# Inject centec sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(CENTEC_SAI)

# Runtime dependency on centec sai is set only for syncd
$(SYNCD)_RDEPENDS += $(CENTEC_SAI)

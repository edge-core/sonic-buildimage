include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/docker-syncd-centec.mk
include $(PLATFORM_PATH)/docker-syncd-centec-rpc.mk
include $(PLATFORM_PATH)/one-image.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/docker-ptf-centec.mk
include $(PLATFORM_PATH)/tsingma-bsp.mk
include $(PLATFORM_PATH)/platform-modules-centec-e530.mk

SONIC_ALL += $(SONIC_ONE_IMAGE) \
             $(DOCKER_FPM)
#             $(DOCKER_SYNCD_CENTEC_RPC)

# Inject centec sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(CENTEC_SAI) $(LIBSAITHRIFT_DEV_CENTEC)

# Runtime dependency on centec sai is set only for syncd
$(SYNCD)_RDEPENDS += $(CENTEC_SAI)

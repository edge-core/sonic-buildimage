include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/docker-syncd-mrvl.mk
include $(PLATFORM_PATH)/docker-syncd-mrvl-rpc.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/one-image.mk

SONIC_ALL += $(SONIC_ONE_IMAGE) \
             $(DOCKER_FPM) \
             $(DOCKER_SYNCD_MRVL_RPC)

# Inject mrvl sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(MRVL_FPA) $(MRVL_SAI)
ifeq ($(ENABLE_SYNCD_RPC),y)
$(LIBSAIREDIS)_DEPENDS += $(LIBSAITHRIFT_DEV_MRVL)
endif

# Runtime dependency on mrvl sai is set only for syncd
$(SYNCD)_RDEPENDS += $(MRVL_SAI)

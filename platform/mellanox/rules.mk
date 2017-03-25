include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/fw.mk
include $(PLATFORM_PATH)/mft.mk
include $(PLATFORM_PATH)/mlnx-sai.mk
include $(PLATFORM_PATH)/hw-management.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx-rpc.mk
include $(PLATFORM_PATH)/docker-orchagent-mlnx.mk
include $(PLATFORM_PATH)/one-image.mk

SONIC_ALL += $(SONIC_ONE_IMAGE) \
             $(DOCKER_FPM_GOBGP) \
             $(DOCKER_SYNCD_MLNX_RPC)

# Inject mlnx sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(MLNX_SAI)

# Runtime dependency on mlnx sai is set only for syncd
$(SYNCD)_RDEPENDS += $(MLNX_SAI)

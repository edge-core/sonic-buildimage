include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/cpld.mk
include $(PLATFORM_PATH)/fw.mk
include $(PLATFORM_PATH)/mft.mk
include $(PLATFORM_PATH)/mlnx-sai.mk
include $(PLATFORM_PATH)/hw-management.mk
include $(PLATFORM_PATH)/mlnx-platform-api.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx-rpc.mk
include $(PLATFORM_PATH)/docker-orchagent-mlnx.mk
include $(PLATFORM_PATH)/docker-saiserver-mlnx.mk
include $(PLATFORM_PATH)/one-image.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/docker-ptf-mlnx.mk
include $(PLATFORM_PATH)/mlnx-sfpd.mk
include $(PLATFORM_PATH)/mlnx-ffb.mk
include $(PLATFORM_PATH)/issu-version.mk

SONIC_ALL += $(SONIC_ONE_IMAGE) \
             $(DOCKER_FPM)

# Inject mlnx sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(MLNX_SAI) $(LIBSAITHRIFT_DEV)

# Runtime dependency on mlnx sai is set only for syncd
$(SYNCD)_RDEPENDS += $(MLNX_SAI)

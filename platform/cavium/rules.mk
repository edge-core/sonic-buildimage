include $(PLATFORM_GENERIC_PATH)/rules.mk

include $(PLATFORM_PATH)/cavm-sai.mk
include $(PLATFORM_PATH)/docker-syncd-cavm.mk
include $(PLATFORM_PATH)/docker-orchagent-cavm.mk

SONIC_ALL += $(DOCKER_SYNCD_CAVM) \
	     $(DOCKER_ORCHAGENT_CAVM)

# Inject cavium sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(CAVM_SAI) $(CAVM_LIBSAI)

# Runtime dependency on cavium sai is set only for syncd
$(SYNCD)_RDEPENDS += $(CAVM_SAI)


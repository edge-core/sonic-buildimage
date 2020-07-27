include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/fw.mk
include $(PLATFORM_PATH)/mft.mk
include $(PLATFORM_PATH)/mlnx-sai.mk
include $(PLATFORM_PATH)/hw-management.mk
include $(PLATFORM_PATH)/mlnx-platform-api.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx.mk
include $(PLATFORM_PATH)/docker-syncd-mlnx-rpc.mk
include $(PLATFORM_PATH)/docker-saiserver-mlnx.mk
include $(PLATFORM_PATH)/one-image.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/docker-ptf-mlnx.mk
include $(PLATFORM_PATH)/mlnx-ffb.mk
include $(PLATFORM_PATH)/issu-version.mk
include $(PLATFORM_PATH)/mlnx-onie-fw-update.mk
include $(PLATFORM_PATH)/mlnx-ssd-fw-update.mk

SONIC_ALL += $(SONIC_ONE_IMAGE) \
             $(DOCKER_FPM)

# Inject mlnx sai into syncd
$(SYNCD)_DEPENDS += $(MLNX_SAI)
$(SYNCD)_UNINSTALLS += $(MLNX_SAI)

ifeq ($(ENABLE_SYNCD_RPC),y)
$(SYNCD)_DEPENDS += $(LIBSAITHRIFT_DEV)
endif

# Runtime dependency on mlnx sai is set only for syncd
$(SYNCD)_RDEPENDS += $(MLNX_SAI)

# Inject mlnx sdk libs to platform monitor
$(DOCKER_PLATFORM_MONITOR)_DEPENDS += $(APPLIBS) $(SX_COMPLIB) $(SXD_LIBS) $(SX_GEN_UTILS) $(PYTHON_SDK_API) $(APPLIBS_DEV) $(SX_COMPLIB_DEV) $(SXD_LIBS_DEV) $(SX_GEN_UTILS_DEV)

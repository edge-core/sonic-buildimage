include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/nephos-modules.mk
include $(PLATFORM_PATH)/platform-modules-ingrasys.mk
include $(PLATFORM_PATH)/platform-modules-accton.mk
include $(PLATFORM_PATH)/platform-modules-cig.mk
include $(PLATFORM_PATH)/docker-syncd-nephos.mk
include $(PLATFORM_PATH)/docker-syncd-nephos-rpc.mk
include $(PLATFORM_PATH)/one-image.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/docker-ptf-nephos.mk

NPX_DIAG = npx_diag
$(NPX_DIAG)_URL = "https://github.com/NephosInc/SONiC/raw/master/sdk/npx_diag"

WARM_VERIFIER = warm-verifier
$(WARM_VERIFIER)_URL = "https://github.com/NephosInc/SONiC/raw/master/sai/warm-verifier"
DSSERVE = dsserve
$(DSSERVE)_URL = "https://sonicstorage.blob.core.windows.net/packages/20170518/dsserve?sv=2015-04-05&sr=b&sig=gyNbgSL%2FvpMXDdpboVkIJcTKMRdGgEaOR9OukHhEsu8%3D&se=2030-03-31T23%3A06%3A35Z&sp=r"

SONIC_ONLINE_FILES += $(NPX_DIAG) $(WARM_VERIFIER) $(DSSERVE)

SONIC_ALL += $(SONIC_ONE_IMAGE) $(DOCKER_FPM)

# Inject nephos sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(NEPHOS_SAI) $(NEPHOS_SAI_DEV)
ifeq ($(ENABLE_SYNCD_RPC),y)
$(LIBSAIREDIS)_DEPENDS += $(LIBSAITHRIFT_DEV)
endif

# Runtime dependency on nephos sai is set only for syncd
$(SYNCD)_RDEPENDS += $(NEPHOS_SAI)

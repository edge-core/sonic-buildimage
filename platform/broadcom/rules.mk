include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/sai.mk
#include $(PLATFORM_PATH)/platform-modules-s6000.mk
#include $(PLATFORM_PATH)/platform-modules-dell.mk
#include $(PLATFORM_PATH)/platform-modules-arista.mk
#include $(PLATFORM_PATH)/platform-modules-ingrasys.mk
#include $(PLATFORM_PATH)/platform-modules-accton.mk
#include $(PLATFORM_PATH)/platform-modules-inventec.mk
#include $(PLATFORM_PATH)/platform-modules-cel.mk
#include $(PLATFORM_PATH)/platform-modules-delta.mk
#include $(PLATFORM_PATH)/platform-modules-quanta.mk
#include $(PLATFORM_PATH)/platform-modules-mitac.mk
include $(PLATFORM_PATH)/docker-orchagent-brcm.mk
include $(PLATFORM_PATH)/docker-syncd-brcm.mk
include $(PLATFORM_PATH)/docker-syncd-brcm-rpc.mk
include $(PLATFORM_PATH)/one-image.mk
include $(PLATFORM_PATH)/raw-image.mk
include $(PLATFORM_PATH)/one-aboot.mk
include $(PLATFORM_PATH)/libsaithrift-dev.mk
include $(PLATFORM_PATH)/python-saithrift.mk
include $(PLATFORM_PATH)/docker-ptf-brcm.mk

BCMCMD = bcmcmd
$(BCMCMD)_URL = "https://sonicstorage.blob.core.windows.net/packages/20170518/bcmcmd?sv=2015-04-05&sr=b&sig=OCW4mfmbQ6D0BH8nllpAWrS8XL9uczrw32w3XgL4jws%3D&se=2030-03-31T23%3A06%3A15Z&sp=r"

DSSERVE = dsserve
$(DSSERVE)_URL = "https://sonicstorage.blob.core.windows.net/packages/20170518/dsserve?sv=2015-04-05&sr=b&sig=gyNbgSL%2FvpMXDdpboVkIJcTKMRdGgEaOR9OukHhEsu8%3D&se=2030-03-31T23%3A06%3A35Z&sp=r"

SONIC_ONLINE_FILES += $(BCMCMD) $(DSSERVE)

SONIC_ALL += $(SONIC_ONE_IMAGE) $(SONIC_ONE_ABOOT_IMAGE) \
             $(DOCKER_FPM)

# Inject brcm sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(BRCM_SAI) $(BRCM_SAI_DEV) $(LIBSAITHRIFT_DEV_BRCM)

# Runtime dependency on brcm sai is set only for syncd
$(SYNCD)_RDEPENDS += $(BRCM_SAI)

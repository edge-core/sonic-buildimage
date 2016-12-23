include $(PLATFORM_GENERIC_PATH)/rules.mk

include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/docker-orchagent-brcm.mk
include $(PLATFORM_PATH)/docker-syncd-brcm.mk

BRCM_DSSERVE = dsserve
$(BRCM_DSSERVE)_PATH = $(PLATFORM_PATH)/sdk
BRCM_BCMCMD = bcmcmd
$(BRCM_BCMCMD)_PATH = $(PLATFORM_PATH)/sdk

SONIC_COPY_FILES += $(BRCM_DSSERVE) $(BRCM_BCMCMD)

SONIC_ALL += $(DOCKER_SYNCD_BRCM) \
	     $(DOCKER_ORCHAGENT_BRCM)

# Inject brcm sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(BRCM_OPENNSL) $(BRCM_SAI) $(BRCM_SAI_DEV)

# Runtime dependency on brcm sai is set only for syncd
$(SYNCD)_RDEPENDS += $(BRCM_OPENNSL) $(BRCM_SAI)

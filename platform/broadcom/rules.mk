include $(PLATFORM_PATH)/sdk.mk
include $(PLATFORM_PATH)/sai.mk
include $(PLATFORM_PATH)/platform-modules-s6000.mk
include $(PLATFORM_PATH)/docker-orchagent-brcm.mk
include $(PLATFORM_PATH)/docker-syncd-brcm.mk
include $(PLATFORM_PATH)/one-image.mk

BCMCMD = bcmcmd
$(BCMCMD)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmcmd?sv=2015-04-05&sr=b&sig=X3bFApmsNFmcnWM9mSGRxBugPcg%2FgJCHh5hhSuV1M2c%3D&se=2030-08-23T14%3A41%3A56Z&sp=r"

DSSERVE = dsserve
$(DSSERVE)_URL = "https://sonicstorage.blob.core.windows.net/packages/dsserve?sv=2015-04-05&sr=b&sig=aMlnRA%2FXZNmHPgmOj%2FNMJMYLWyvva1QrN4HcsVXvqKA%3D&se=2030-08-23T14%3A42%3A32Z&sp=r"

SONIC_ONLINE_FILES += $(BCMCMD) $(DSSERVE)

SONIC_ALL += $(SONIC_ONE_IMAGE)

# Inject brcm sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(BRCM_OPENNSL) $(BRCM_SAI) $(BRCM_SAI_DEV)

# Runtime dependency on brcm sai is set only for syncd
$(SYNCD)_RDEPENDS += $(BRCM_OPENNSL) $(BRCM_SAI)

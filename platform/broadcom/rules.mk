OPENNSL = libopennsl_6.4.11-1+0~20160719212144.23~1.gbp8ec2d1_amd64.deb
$(OPENNSL)_PATH = $(PLATFORM_PATH)/brcm_sdk
BRCM_SAI = libsaibcm_1.0.2~20160727172452.52_amd64.deb
$(BRCM_SAI)_PATH = $(PLATFORM_PATH)/brcm_sdk
BRCM_SAI_DBG = libsaibcm-dbg_1.0.2~20160727172452.52_amd64.deb
$(BRCM_SAI_DEV)_PATH = $(PLATFORM_PATH)/brcm_sdk
BRCM_SAI_DEV = libsaibcm-dev_1.0.2~20160727172452.52_amd64.deb
$(BRCM_SAI_DBG)_PATH = $(PLATFORM_PATH)/brcm_sdk

SONIC_COPY_DEBS += $(OPENNSL) $(BRCM_SAI) $(BRCM_SAI_DBG) $(BRCM_SAI_DEV)

# TODO: Put dependencies for SDK packages

SONIC_ALL += $(SONIC_GENERIC) $(DOCKER_SYNCD) $(DOCKER_ORCHAGENT) $(DOCKER_FPM)

# Inject brcm sai into sairedis
$(LIBSAIREDIS)_DEPENDS += $(BRCM_LIBSAI)

# Runtime dependency on brcm sai is set only for syncd
$(SYNCD)_RDEPENDS += $(BRCM_LIBSAI)

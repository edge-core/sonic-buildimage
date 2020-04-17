BRCM_SAI = libsaibcm_3.7.3.3-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.3.3-4_amd64.deb?sv=2015-04-05&sr=b&sig=9z7vLhweD%2B%2FZylkr9XsDAJ3DdE5NJlcPTslFYyBuAXU%3D&se=2033-12-25T14%3A52%3A25Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.3.3-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.3.3-4_amd64.deb?sv=2015-04-05&sr=b&sig=SAOoGh2zdljiPuKeDoa%2B1lSJzZ8uXh2Irl2RZX1uAiA%3D&se=2033-12-25T14%3A53%3A44Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

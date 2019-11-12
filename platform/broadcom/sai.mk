BRCM_SAI = libsaibcm_3.5.3.1m-25_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm_3.5.3.1m-26_amd64.deb?sv=2015-04-05&sr=b&sig=zo83IKnlT7goymXwynW8%2Fx6rR2eIh0AiIS%2BSrSMUhRE%3D&se=2033-07-21T18%3A50%3A27Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.1m-25_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dev_3.5.3.1m-26_amd64.deb?sv=2015-04-05&sr=b&sig=tQmkCIy2mnb9rH7B9oXFUZDwijMGXWnVtta2CNTMbFM%3D&se=2033-07-21T18%3A50%3A47Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

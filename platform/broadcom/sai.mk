BRCM_SAI = libsaibcm_3.3.5.4m-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.5.4m-1_amd64.deb?sv=2015-04-05&sr=b&sig=5al8VoedFxE3anjfi4BwLLX2YqU%2BByafkZgEY85TnN8%3D&se=2032-12-17T20%3A59%3A24Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.5.4m-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.5.4m-1_amd64.deb?sv=2015-04-05&sr=b&sig=ROLknrDMqOGeGfOXu8%2BUVl8yKKDyxsq3swiUtR7n63A%3D&se=2032-12-17T20%3A58%3A59Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

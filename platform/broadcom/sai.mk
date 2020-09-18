BRCM_SAI = libsaibcm_3.5.3.5-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=MbN7UziViFCHGemjYicnN9NBitcgiasBZFwTDEAaxkk%3D&se=2034-05-18T22%3A40%3A56Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.5-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.5-2_amd64.deb?sv=2015-04-05&sr=b&sig=JICIoChs68GfIgWDmrrcMvrTlrZaXEkMzc0hkan0NUM%3D&se=2034-05-18T22%3A40%3A30Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

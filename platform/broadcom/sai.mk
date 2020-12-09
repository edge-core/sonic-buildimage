BRCM_SAI = libsaibcm_4.2.1.5-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm_4.2.1.5-6_amd64.deb?sv=2015-04-05&sr=b&sig=%2BZXgixWQWbDP5gEEID4wmkAT2vB%2FW%2BAiDIHs9z1FuZQ%3D&se=2034-08-18T02%3A06%3A57Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm-dev_4.2.1.5-6_amd64.deb?sv=2015-04-05&sr=b&sig=fGd05XpZ%2FuIJ6UP7Cr39Ctz8%2Bnh4e6O6gqXFdgOTok0%3D&se=2034-08-18T02%3A06%3A24Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

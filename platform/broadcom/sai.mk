BRCM_SAI = libsaibcm_4.2.1.5-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm_4.2.1.5-4_amd64.deb?sv=2015-04-05&sr=b&sig=dHfQf95FxgLBlnrGJwv6pIkAYAc6mOGbz9vvUMfxFvg%3D&se=2034-07-28T05%3A53%3A21Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm-dev_4.2.1.5-4_amd64.deb?sv=2015-04-05&sr=b&sig=n98j842RZy%2BwQh4CtOku7jz6wgV%2BusbTl9NkeRndBrE%3D&se=2037-01-13T05%3A54%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

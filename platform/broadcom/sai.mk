BRCM_SAI = libsaibcm_4.3.3.5-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=WHmBcthD%2FqBv4Pia0GH4GQ%2BdKm8rolG8dJSh%2BYoGEr8%3D&se=2035-01-12T01%3A52%3A20Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.5-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=BcGHyOGfS%2FypmiNUtHnX8WCbUwqoXPiRRe9E%2FUl9Sp8%3D&se=2035-01-12T01%3A52%3A57Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

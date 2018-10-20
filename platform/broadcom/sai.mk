BRCM_SAI = libsaibcm_3.1.3.5-11_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-11_amd64.deb?sv=2015-04-05&sr=b&sig=gATwARdB%2FH42%2FUYDirrHcqXzGfSDq79IP4LMVgjUuo0%3D&se=2155-09-02T04%3A33%3A51Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-11_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-11_amd64.deb?sv=2015-04-05&sr=b&sig=YE%2BCpURwLGSzE8qBVandbERncFUkm5CEvCdMB9YrKZM%3D&se=2155-09-02T02%3A43%3A51Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

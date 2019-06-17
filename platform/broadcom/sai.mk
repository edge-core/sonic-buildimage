BRCM_SAI = libsaibcm_3.5.2.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=anY6TeLouYsw7L6hfpH%2BTHOkvF8M3WR%2B6P2C7Dh8sHg%3D&se=2033-02-20T17%3A19%3A46Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.2.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dev_3.5.2.3_amd64.deb?sv=2015-04-05&sr=b&sig=o%2BVIKwVnlNv8LAvVzcS2kIXc0%2BIKaTzmA8LIkIfsh6c%3D&se=2033-02-20T17%3A20%3A03Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

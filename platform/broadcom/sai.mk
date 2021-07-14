BRCM_SAI = libsaibcm_4.3.3.9_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.9_amd64.deb?sv=2015-04-05&sr=b&sig=UgZ4pYi9Q5mSK6QLlDCkz%2Br3u0WBdbS28K5apa0RmgQ%3D&se=2035-03-23T05%3A31%3A58Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.9_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.9_amd64.deb?sv=2015-04-05&sr=b&sig=yQJG%2Fy%2BRyxbgHXERIHMeHDGcy%2BSjV%2BFeCTop9wfW5hQ%3D&se=2035-03-23T05%3A33%3A01Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

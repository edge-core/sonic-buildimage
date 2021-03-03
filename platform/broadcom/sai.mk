BRCM_SAI = libsaibcm_4.3.3.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.3.1_amd64.deb?sv=2019-12-12&st=2021-03-03T00%3A35%3A37Z&se=2030-03-04T00%3A35%3A00Z&sr=b&sp=r&sig=1miXMYs0%2BZ6v9Dpby1vSYsDezWDnr%2Be4gZ7Gi3kAQXE%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.3.1_amd64.deb?sv=2019-12-12&st=2021-03-03T00%3A37%3A16Z&se=2030-03-04T00%3A37%3A00Z&sr=b&sp=r&sig=xxnhJC%2FKsOvApuAlB1Yds8Uzzkdyy6fmWX%2BuJ4v0UYA%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

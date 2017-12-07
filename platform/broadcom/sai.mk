BRCM_SAI = libsaibcm_3.0.3.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.3_amd64.deb?sv=2015-04-05&sr=b&sig=itlsEt8vqhWfZzuq%2FOSWSGgHN5kokf5a9AYOSJhD3t4%3D&se=2031-08-16T03%3A11%3A13Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.3_amd64.deb?sv=2015-04-05&sr=b&sig=0DXLHgPXuMHERp44qJNNdQyYSv969sQsY7USCL6gCRw%3D&se=2031-08-16T03%3A10%3A49Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

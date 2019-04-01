BRCM_SAI = libsaibcm_3.3.4.3m-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm_3.3.4.3m-3_amd64.deb?sv=2015-04-05&sr=b&sig=QpwawYAGZOdlH6Z7PLOlHSl%2B%2Fcqe0IrDAq2a7hlmFmg%3D&se=2156-01-09T02%3A48%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.3.4.3m-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.3/libsaibcm-dev_3.3.4.3m-3_amd64.deb?sv=2015-04-05&sr=b&sig=8CYNbomcJhVI%2BFdIUN%2F1rIOM%2BwwMzn33Lb8Llgo8GsY%3D&se=2156-01-09T02%3A49%3A03Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

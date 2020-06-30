BRCM_SAI = libsaibcm_3.7.5.1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=hZLFA8GbuY83MW9g2ggfe53ATx9riuyL1JYXIe1Bib4%3D&se=2034-03-04T00%3A08%3A23Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.5.1_amd64.deb?sv=2015-04-05&sr=b&sig=i5GcJ8ATr4NL5iLth6DrX8YXxe7ir5OsXN7fxJISvCE%3D&se=2034-03-04T00%3A09%3A48Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

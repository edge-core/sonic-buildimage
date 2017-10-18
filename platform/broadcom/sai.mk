BRCM_SAI = libsaibcm_3.0.3.2-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-7_amd64.deb?sv=2015-04-05&sr=b&sig=RUUm3WJuGYmtIatkKtR5iAuI%2FG2KM9hMXewAEnR2AKY%3D&se=2031-06-26T21%3A45%3A55Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-7_amd64.deb?sv=2015-04-05&sr=b&sig=hTQZeaqa7oiR9YTIuUGG1DGYNg8bwlWKB2J2r46Mq%2BE%3D&se=2031-06-26T21%3A46%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

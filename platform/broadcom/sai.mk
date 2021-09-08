BRCM_SAI = libsaibcm_5.0.0.8_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.8_amd64.deb?sv=2015-04-05&sr=b&sig=T%2FPesnOIeN9802mClMpgk8XFQbqjFAgCnJbbNHxijHo%3D&se=2035-05-13T21%3A34%3A26Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.8_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.8_amd64.deb?sv=2015-04-05&sr=b&sig=X33hZLhRI3L6f4a5JFSlhJvoaTj%2B3zrmNBM9IzIA%2Bj4%3D&se=2035-05-13T21%3A35%3A58Z&sp=r"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.8_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.8_amd64.deb?sv=2015-04-05&sr=b&sig=uy0OW6ZhWjYntalZunEIIzHUztkOyI7TS3F73Sla9vY%3D&se=2035-05-13T21%3A37%3A06Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

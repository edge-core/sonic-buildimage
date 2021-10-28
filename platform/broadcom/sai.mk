BRCM_SAI = libsaibcm_6.0.0.10_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/libsaibcm_6.0.0.10_amd64.deb?sv=2020-08-04&st=2021-10-20T15%3A46%3A03Z&se=2030-10-21T15%3A46%3A00Z&sr=b&sp=r&sig=zhosphas9cBuH%2B7mLC%2ByarQPQSIe2LY%2FXOATIW96cVY%3D"
BRCM_SAI_DEV = libsaibcm-dev_6.0.0.10_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/libsaibcm-dev_6.0.0.10_amd64.deb?sv=2020-08-04&st=2021-10-20T15%3A47%3A11Z&se=2030-10-21T15%3A47%3A00Z&sr=b&sp=r&sig=pKZxnQKw%2BY6CzAd8swa5yZDduKIrQw7TWyChT5tkqlk%3D"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_6.0.0.10_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/6.0/master/libsaibcm_dnx_6.0.0.10_amd64.deb?sv=2020-08-04&st=2021-10-20T15%3A48%3A05Z&se=2030-10-21T15%3A48%3A00Z&sr=b&sp=r&sig=1sqJI5dLLrci9iu%2FPhNWZJzj0nf5lmcRrAUkASOQVjo%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

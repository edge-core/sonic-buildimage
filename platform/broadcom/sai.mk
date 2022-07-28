BRCM_SAI = libsaibcm_3.7.6.1-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.6.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=feV68rm1rnQzVyEFQjE5ceusSIqtIzlyUX7mPEmio%2B0%3D&se=2038-12-30T22%3A23%3A47Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.6.1-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.6.1-2_amd64.deb?sv=2015-04-05&sr=b&sig=80L3rvMTgilj61D4HCLKOjE2of2SgZF3128JmHYTunc%3D&se=2038-12-30T22%3A24%3A53Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_3.7.5.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm_3.7.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=vSaGIDz2fHBtQXmwJ8OrulAF1N%2Bwk%2B51CkqwNiZFx6I%3D&se=2034-03-10T00%3A45%3A39Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.5.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/master/libsaibcm-dev_3.7.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=XpczZg8q3b2z3754wXdc4faOXOFofdlydJKEQaed01o%3D&se=2034-03-10T00%3A46%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

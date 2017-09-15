BRCM_SAI = libsaibcm_3.0.3.2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2_amd64.deb?sv=2015-04-05&sr=b&sig=d50c3WTnlQGVgybK4RyNFWqvXPHPpAotNSongSABpWg%3D&se=2031-05-25T18%3A52%3A35Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2_amd64.deb?sv=2015-04-05&sr=b&sig=psB%2BzhbludRstCuuGncrMOg5oETOY13U26yEXyR2yWc%3D&se=2031-05-25T18%3A50%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

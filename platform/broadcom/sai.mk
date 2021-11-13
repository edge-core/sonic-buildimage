BRCM_SAI = libsaibcm_4.3.5.1-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-7_amd64.deb?sv=2015-04-05&sr=b&sig=DWwsbdvPdUHTB0x%2B5ZK%2Bp1qjqJ4TDb1FV0az09K5pXo%3D&se=2035-07-23T07%3A51%3A17Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-7_amd64.deb?sv=2015-04-05&sr=b&sig=jZaZP84GRkdZiu%2BtoS7n7K3RC8vf%2FD1ZwnHq5vNeHGA%3D&se=2035-07-23T07%3A52%3A20Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

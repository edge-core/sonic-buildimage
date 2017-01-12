BRCM_SAI = libsaibcm_2.0.3.7-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.0.3.7-2_amd64.deb?sv=2015-04-05&sr=b&sig=E9zdq7DpvZSpztO94eiNF4svl8T3wCywZxXRLpLnIpk%3D&se=2030-09-21T00%3A27%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.0.3.7-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.0.3.7-2_amd64.deb?sv=2015-04-05&sr=b&sig=I11bX9%2Fo%2F2v1e0KGOnC9pN2MkDcQQZLUGtIJF8rE65w%3D&se=2030-09-21T00%3A28%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

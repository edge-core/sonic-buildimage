BRCM_SAI = libsaibcm_4.3.0.10-4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm_4.3.0.10-4_amd64.deb?sv=2015-04-05&sr=b&sig=nfseU56PACVqklQ4MC0HvZ7qt7Ou4loQMBA7jx8CSOY%3D&se=2034-10-13T16%3A31%3A22Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.0.10-4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/master/libsaibcm-dev_4.3.0.10-4_amd64.deb?sv=2015-04-05&sr=b&sig=4tF26GxI6jmrcvRyCezQ7RL6qMjzip7SFf61eqy%2Bvf4%3D&se=2034-10-13T16%3A31%3A53Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

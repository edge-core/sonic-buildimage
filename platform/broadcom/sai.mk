BRCM_SAI = libsaibcm_4.2.1.5-7_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm_4.2.1.5-8_amd64.deb?sv=2019-12-12&st=2020-12-18T18%3A41%3A23Z&se=2030-12-19T18%3A41%3A00Z&sr=b&sp=r&sig=GFNMn0borytUTFQJf%2F5A0J452XsQ%2FqnzBw5GyjFuYHw%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-7_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm-dev_4.2.1.5-8_amd64.deb?sv=2019-12-12&st=2020-12-18T18%3A42%3A03Z&se=2030-12-19T18%3A42%3A00Z&sr=b&sp=r&sig=J%2BbRtZVVcZTLs3uqzZs9zObLKFxRgzvJkFL5iyJ48mA%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

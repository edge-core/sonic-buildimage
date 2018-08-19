BRCM_SAI = libsaibcm_3.1.3.5-6_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-6_amd64.deb?sv=2015-04-05&sr=b&sig=Srm9zk6mYTYpqaifRwrMwQ9%2Bqf2b0HqrkS9okhSA%2Bq0%3D&se=2155-07-11T19%3A40%3A27Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-6_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-6_amd64.deb?sv=2015-04-05&sr=b&sig=xqMANzXnUJli4hcggZ8wJpepxfCaWedW2%2Fyx3X%2BXDH4%3D&se=2155-07-11T19%3A40%3A50Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

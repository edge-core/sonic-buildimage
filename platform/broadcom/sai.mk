BRCM_SAI = libsaibcm_3.5.3.5-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.5-3_amd64.deb?sv=2019-10-10&st=2020-10-28T16%3A16%3A17Z&se=2040-10-29T16%3A16%3A00Z&sr=b&sp=r&sig=g57JqV9YzbGXegUvCCjSht4A59zZP3I01CA6X%2Bh4J80%3D"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.5-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.5-3_amd64.deb?sv=2019-10-10&st=2020-10-28T16%3A14%3A38Z&se=2040-10-29T16%3A14%3A00Z&sr=b&sp=r&sig=ZgAYr3cUmpxJgsnNezW8x6cbB%2B6uDQQdG%2BW1BsALeIM%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

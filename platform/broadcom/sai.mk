BRCM_SAI = libsaibcm_3.5.3.5-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm_3.5.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=eZe9zHqIQPE9iC9qqfKo1mtEUN8t21Knk3rTJiBCBNk%3D&se=2034-02-16T17%3A02%3A25Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.5-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/jessie/libsaibcm-dev_3.5.3.5-1_amd64.deb?sv=2015-04-05&sr=b&sig=uGQ9jcEbi7oyowp7YkCkBjFmR0pYuYeeAdPcWa8Z7zo%3D&se=2034-02-16T17%3A02%3A03Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

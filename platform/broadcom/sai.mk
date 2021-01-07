BRCM_SAI = libsaibcm_4.2.1.5-9_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm_4.2.1.5-9_amd64.deb?sv=2015-04-05&sr=b&sig=Rbqq%2FH4B71%2BWGzAzTuM3qxEdwpEnuxqFdGIMDpuN8t0%3D&se=2034-09-16T01%3A36%3A13Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.5-9_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/buster/libsaibcm-dev_4.2.1.5-9_amd64.deb?sv=2015-04-05&sr=b&sig=C%2Bo7YTkA2076LRfet1rHHlFu%2F6b9qoQiHljjaZCVa20%3D&se=2034-09-16T01%3A37%3A38Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

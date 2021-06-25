BRCM_SAI = libsaibcm_4.3.3.8-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.8-1_amd64.deb?sv=2015-04-05&sr=b&sig=gfKgP7HePZcvoESly6xJ%2BIyTovF%2BWZvyvTjfWR%2BqMcs%3D&se=2035-03-04T06%3A55%3A34Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.8-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.8-1_amd64.deb?sv=2015-04-05&sr=b&sig=ST85a0laEY245n2QAy5gtbpd8LZkIuCSiBDEVc10wC8%3D&se=2035-03-04T06%3A57%3A04Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

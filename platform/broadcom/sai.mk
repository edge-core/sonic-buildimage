BRCM_SAI = libsaibcm_3.0.3.2-10_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-10_amd64.deb?sv=2015-04-05&sr=b&sig=tByZ7QDBsYlJ4UHbapnzqHYrbA8rD92%2FQXEpupITTmM%3D&se=2031-07-06T19%3A19%3A32Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-10_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-10_amd64.deb?sv=2015-04-05&sr=b&sig=T6U8sF%2BW8B%2FffBzPoUJ9peLcg2O9MunHBBKSu7SZOKo%3D&se=2031-07-06T19%3A19%3A52Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

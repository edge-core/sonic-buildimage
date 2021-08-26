BRCM_SAI = libsaibcm_4.3.5.1-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=lQsSB%2BJnoynyjbrRl30QSWKsl5qb7kVq9L9DB%2BhZeP4%3D&se=2035-05-05T06%3A04%3A02Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-1_amd64.deb?sv=2015-04-05&sr=b&sig=2YjE1nTWN5Nr5403N4kYge1kSvgGtE3t87HY7FsGKeo%3D&se=2035-05-05T06%3A05%3A03Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

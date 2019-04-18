BRCM_SAI = libsaibcm_3.1.3.4-21_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.4-21_amd64.deb?sv=2015-04-05&sr=b&sig=KH4pkYsvmZ2q99k8JX09Zw94dKSr7HMdKznM0eQtyeM%3D&se=2032-12-24T23%3A36%3A03Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-21_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.4-21_amd64.deb?sv=2015-04-05&sr=b&sig=dKIUB%2BvmJsgw%2FlYa5wGvEL%2FyhbyXwYd5hXrBSXDux5M%3D&se=2032-12-24T23%3A36%3A19Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

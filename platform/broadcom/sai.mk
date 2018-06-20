BRCM_SAI = libsaibcm_3.1.3.4-14_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-14_amd64.deb?sv=2015-04-05&sr=b&sig=RUib2nzuTwstNgT9OJ6DGv5OraWc6oyOmMtaRh6pDdw%3D&se=2032-02-25T17%3A38%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-14_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-14_amd64.deb?sv=2015-04-05&sr=b&sig=GRdByGTrNZbZoQmXhsVC%2BL7ZeDwzstl4Vq6vGssrmyo%3D&se=2032-02-25T17%3A39%3A09Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

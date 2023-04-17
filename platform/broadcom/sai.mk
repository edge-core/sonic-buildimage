BRCM_SAI = libsaibcm_3.7.6.1-3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.6.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=UT0aePCjoT%2Fu0dtTgoGUgvzSJSN8DPh62jDm%2FECPkQA%3D&se=2026-07-30T17%3A27%3A51Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.6.1-3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.6.1-3_amd64.deb?sv=2015-04-05&sr=b&sig=Cd5GpQyd5epuMD%2BGuprH79IK8ZWlX5T9dAoL7j23Ceo%3D&se=2026-07-30T17%3A29%3A46Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

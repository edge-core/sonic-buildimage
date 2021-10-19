BRCM_SAI = libsaibcm_4.3.5.1-5_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.1-5_amd64.deb?sv=2015-04-05&sr=b&sig=TpNMP8d%2BuTseukC%2BbiqS1JAsw0mKNCF1dtJOcSC4ydk%3D&se=2035-06-27T06%3A29%3A36Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.1-5_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.1-5_amd64.deb?sv=2015-04-05&sr=b&sig=M%2FAiNWLGFMMzLHGJBPpZ%2B18JTYcOFPgHYtKLhkvO0r4%3D&se=2035-06-27T06%3A30%3A28Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_4.3.5.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.5.3_amd64.deb?sv=2020-10-02&st=2022-01-20T07%3A18%3A38Z&se=2037-01-21T07%3A18%3A00Z&sr=b&sp=r&sig=Xc%2B21qOoubU55yoOL7S98Ry%2BHPij2Hbp3p5kNmDPl9U%3D"
BRCM_SAI_DEV = libsaibcm-dev_4.3.5.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.5.3_amd64.deb?sv=2020-10-02&st=2022-01-20T07%3A20%3A23Z&se=2037-01-21T07%3A20%3A00Z&sr=b&sp=r&sig=cNpi1ooWSSJW%2FcxjUTKxMgQ%2FM%2FOO6AE%2BG8UYcTA%2FxVA%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

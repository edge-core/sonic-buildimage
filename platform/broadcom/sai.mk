BRCM_SAI = libsaibcm_2.1.5.1-2-20170419194756.21_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-2-20170419194756.21_amd64.deb?sv=2015-04-05&sr=b&sig=On9N1tlOSbYj%2Fb0JudmUjYRTbvS5cvqcGJUEIDX8wzk%3D&se=2030-12-27T20%3A56%3A24Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-2-20170419194756.21_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-2-20170419194756.21_amd64.deb?sv=2015-04-05&sr=b&sig=iVQRbQUTmeKqd01pMMR%2FIwlEUsAeiGIxCrqfr24lQ8k%3D&se=2030-12-27T20%3A57%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

BRCM_SAI = libsaibcm_2.1.5.1-5-20170505222214.31_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-5-20170505222214.31_amd64.deb?sv=2015-04-05&sr=b&sig=jxKRlFJ%2BjDmq6Xi2p1SXc35IVdhsfRoR0umcOnM5Cj8%3D&se=2031-01-12T22%3A43%3A54Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-5-20170505222214.31_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-5-20170505222214.31_amd64.deb?sv=2015-04-05&sr=b&sig=HZN4itbQuJXfZCPZx1A%2BSxN3hBxZ05%2FmCE8Lp1zTgXM%3D&se=2031-01-12T22%3A44%3A20Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

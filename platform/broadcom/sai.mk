BRCM_SAI = libsaibcm_2.0.3.7-3-20170118215303.119_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.0.3.7-3-20170118215303.119_amd64.deb?sv=2015-04-05&sr=b&sig=lmAbkYBRtlEDUwFxAGK0bpGOZ3QIrgzrF3WD%2Ba2tvvY%3D&se=2030-09-27T22%3A51%3A39Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.0.3.7-3-20170118215303.119_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.0.3.7-3-20170118215303.119_amd64.deb?sv=2015-04-05&sr=b&sig=e8tPGsXcOfVtMpQdwZKNOpHplezroAkIfxASfK%2BJDR8%3D&se=2030-09-27T22%3A49%3A47Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

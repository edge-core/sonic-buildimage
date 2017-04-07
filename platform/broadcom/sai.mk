BRCM_SAI = libsaibcm_2.1.5.1-1-20170407044929.18_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-1-20170407044929.18_amd64.deb?sv=2015-04-05&sr=b&sig=lKKP8Ot01SW9NwbbnafZly5rTkIK2rpTdBuUwcWdr5U%3D&se=2030-12-15T04%3A51%3A54Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-1-20170407044929.18_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-1-20170407044929.18_amd64.deb?sv=2015-04-05&sr=b&sig=AsDdE0zR3aTxwdK76Iro0jGypl%2FSqVoYmwz0drr78Ho%3D&se=2030-12-15T04%3A52%3A31Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

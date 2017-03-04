BRCM_SAI = libsaibcm_2.1.5.1-20170303234832.14_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-20170303234832.14_amd64.deb?sv=2015-04-05&sr=b&sig=gZKsefmpU6Xc6X0emxjlGKwf1aPsyxloulhXL0qGgFc%3D&se=2030-11-10T23%3A58%3A37Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-20170303234832.14_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-20170303234832.14_amd64.deb?sv=2015-04-05&sr=b&sig=kEhXcoL0iOUpnuGJLduktluImi0eQVHAjGunGbipa28%3D&se=2030-11-10T23%3A59%3A08Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

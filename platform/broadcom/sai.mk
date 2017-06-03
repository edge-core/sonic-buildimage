BRCM_SAI = libsaibcm_2.1.5.1-10-20170602191744.42_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-10-20170602191744.42_amd64.deb?sv=2015-04-05&sr=b&sig=aSmyd3pgiI2LkssoqGY6PDDhFKvWS2RxFB%2Bcpe%2FRiCg%3D&se=2031-02-09T19%3A29%3A48Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-10-20170602191744.42_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-10-20170602191744.42_amd64.deb?sv=2015-04-05&sr=b&sig=NSJ96np%2FHmXJdMN3Dnzp8UHBlo4OUiG00ETejp7wARI%3D&se=2031-02-09T19%3A30%3A14Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

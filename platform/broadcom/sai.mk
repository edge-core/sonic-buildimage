BRCM_SAI = libsaibcm_2.1.5.1-8-20170531021119.40_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-8-20170531021119.40_amd64.deb?sv=2015-04-05&sr=b&sig=rFP9dZ9aXpe3CN5jBVNo6rkgK94%2BJFzMiXd1I2954lU%3D&se=2031-02-07T02%3A13%3A20Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-8-20170531021119.40_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-8-20170531021119.40_amd64.deb?sv=2015-04-05&sr=b&sig=m5AGCyfLkcYvv8xmY6gPZFiXmygYLQUGfFrEiMO8Jtk%3D&se=2031-02-07T02%3A13%3A55Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

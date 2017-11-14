BRCM_SAI = libsaibcm_3.0.3.2-12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-12_amd64.deb?sv=2015-04-05&sr=b&sig=iIHm3VuMr%2BcvLP4Mcq0I90JUmxuw35%2FbktTwt13%2FqbE%3D&se=2031-07-23T23%3A48%3A11Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-12_amd64.deb?sv=2015-04-05&sr=b&sig=Guh0wkJFpWssS10eiwxeuzAOQEsAtbdfVzpRS%2F9uC6k%3D&se=2031-07-23T23%3A48%3A26Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

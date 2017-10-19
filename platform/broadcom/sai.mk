BRCM_SAI = libsaibcm_3.0.3.2-8_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.0.3.2-8_amd64.deb?sv=2015-04-05&sr=b&sig=PYRdEo1SB0TfoahBoxwoNMt4g1V5aQpBH5RolBGZ6Lw%3D&se=2031-06-28T20%3A29%3A10Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.0.3.2-8_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.0.3.2-8_amd64.deb?sv=2015-04-05&sr=b&sig=HWoCzzgNscATWcW0KXjh24LdoJ0AM4sVgISgyBh60MI%3D&se=2031-06-28T20%3A28%3A29Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

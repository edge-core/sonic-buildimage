BRCM_SAI = libsaibcm_4.3.3.8_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm_4.3.3.8_amd64.deb?sv=2015-04-05&sr=b&sig=OPgORcuUzFLJdt9VwqnZuRx2TgGUo5tbDIOtpJuoHB4%3D&se=2035-02-25T22%3A17%3A13Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.3.3.8_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.3/202012/libsaibcm-dev_4.3.3.8_amd64.deb?sv=2015-04-05&sr=b&sig=2N3yC%2BDAXt%2BN98V5Qc8cxBV7V%2FE%2B4C%2BYTSzs0d3MIOA%3D&se=2035-02-25T22%3A17%3A52Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

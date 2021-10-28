BRCM_SAI = libsaibcm_5.0.0.11_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.11_amd64.deb?sv=2020-04-08&st=2021-10-11T23%3A05%3A48Z&se=2026-01-13T00%3A05%3A00Z&sr=b&sp=r&sig=ibf4R3MH4eb9IVdf%2F8iN6tvYjxroPaxRub7oIGdRxSI%3D"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.11_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.11_amd64.deb?sv=2020-04-08&st=2021-10-11T23%3A06%3A45Z&se=2026-01-13T00%3A06%3A00Z&sr=b&sp=r&sig=LXhLM8%2Bfu%2B9ywI49nSrs4TBy1w5CY0e6CRyv1dLwJnI%3D"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.11_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.11_amd64.deb?sv=2020-04-08&st=2021-10-11T23%3A07%3A43Z&se=2026-01-13T00%3A07%3A00Z&sr=b&sp=r&sig=p1kqeugBvmdeggplqYk%2FY2nHTkwrTg6KTeNUYotfDyc%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_5.0.0.12_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-23T00%3A21%3A32Z&se=2022-02-24T00%3A21%3A32Z&sr=b&sp=r&sig=oIdQH3MKoPBoaVw1mZtH78%2FhmcwIHLgdcJPJmWA%2B22s%3D"

BRCM_SAI_DEV = libsaibcm-dev_5.0.0.12_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-23T00%3A22%3A55Z&se=2022-02-24T00%3A22%3A55Z&sr=b&sp=r&sig=9qjEwMtJghg4LT1VbMV6mUI%2BWTPolFbsSUg688MSpBI%3D"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.12_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.12_amd64.deb?sv=2020-10-02&st=2022-02-23T00%3A24%3A00Z&se=2024-02-24T00%3A24%3A00Z&sr=b&sp=r&sig=37ps6%2FOHfjfPK8gISP0K2VMF9Djq%2FedZM24Vj4ALNH8%3D"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

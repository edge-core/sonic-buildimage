BRCM_SAI = libsaibcm_5.0.0.4_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_5.0.0.4_amd64.deb?sv=2015-04-05&sr=b&sig=ZuEkoLskVsCtNoej4I%2BBuhX01hFJXZC4yuhoFg0jzuw%3D&se=2035-03-21T23%3A30%3A55Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_5.0.0.4_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm-dev_5.0.0.4_amd64.deb?sv=2015-04-05&sr=b&sig=JYxPob3rO%2BnPv%2FTFn9Q3xbVx5l6ZxwrRq7fpg%2BcUqwQ%3D&se=2035-03-21T23%3A31%3A26Z&sp=r"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_5.0.0.4_amd64.deb
$(BRCM_DNX_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/5.0/master/libsaibcm_dnx_5.0.0.4_amd64.deb?sv=2015-04-05&sr=b&sig=CNtYmID5aZtc0ZFHldWYCQSbzyb9xT18vGxT%2BZj7kHc%3D&se=2035-03-21T23%3A31%3A50Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

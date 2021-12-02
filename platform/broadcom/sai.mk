LIBSAIBCM_VERSION = 6.0.0.10-1
LIBSAIBCM_BRANCH_NAME = REL_6.0
LIBSAIBCM_URL_PREFIX = "https://sonicstorage.blob.core.windows.net/public/sai/bcmsai/$(LIBSAIBCM_BRANCH_NAME)/$(LIBSAIBCM_VERSION)"

BRCM_SAI = libsaibcm_$(LIBSAIBCM_VERSION)_amd64.deb
$(BRCM_SAI)_URL = "$(LIBSAIBCM_URL_PREFIX)/$(BRCM_SAI)"
BRCM_SAI_DEV = libsaibcm-dev_$(LIBSAIBCM_VERSION)_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "$(LIBSAIBCM_URL_PREFIX)/$(BRCM_SAI_DEV)"

# SAI module for DNX Asic family
BRCM_DNX_SAI = libsaibcm_dnx_$(LIBSAIBCM_VERSION)_amd64.deb
$(BRCM_DNX_SAI)_URL = "$(LIBSAIBCM_URL_PREFIX)/$(BRCM_DNX_SAI)"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
SONIC_ONLINE_DEBS += $(BRCM_DNX_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

BRCM_SAI = libsaibcm_3.1.3.5-10_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm_3.1.3.5-10_amd64.deb?sv=2015-04-05&sr=b&sig=knKdBT4t%2B%2F8JvPe5wfCJPsJ1JU1kSsCBzMBFQHtXoAg%3D&se=2032-05-30T19%3A33%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.5-10_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/libsaibcm-dev_3.1.3.5-10_amd64.deb?sv=2015-04-05&sr=b&sig=aYTN5yyq9dy4uz%2FctVXhuG9qqLs%2FefT4lJFmheRAk7I%3D&se=2032-05-30T19%3A34%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

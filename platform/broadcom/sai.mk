BRCM_SAI = libsaibcm_4.2.1.3_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm_4.2.1.3_amd64.deb?sv=2015-04-05&sr=b&sig=aA0Ltk2jteFuJZdr1ldj%2F5e6o7R0U5S%2FqVWvutPC7k0%3D&se=2021-08-31T04%3A08%3A35Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_4.2.1.3_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/4.2/master/libsaibcm-dev_4.2.1.3_amd64.deb?sv=2015-04-05&sr=b&sig=r%2FWgs1VEFo07sbfYK%2FDZmk83QKTzwSSe%2F3%2BN3k3uAcY%3D&se=2022-01-30T22%3A55%3A04Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
$(eval $(call add_conflict_package,$(BRCM_SAI_DEV),$(LIBSAIVS_DEV)))

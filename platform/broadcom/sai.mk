BRCM_SAI = libsaibcm_2.1.5.1-11-20170605231900.43_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-11-20170605231900.43_amd64.deb?sv=2015-04-05&sr=b&sig=NNBDS1OSXn2w4dNSbqBbJnqXTrqH7YAkKIa%2Fi9yaOJs%3D&se=2031-02-12T23%3A22%3A01Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-11-20170605231900.43_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-11-20170605231900.43_amd64.deb?sv=2015-04-05&sr=b&sig=jxozueiuQdOuJdEfC9%2BWSfFXSL68FQVwL%2FM5Obfj3gs%3D&se=2031-02-12T23%3A21%3A35Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

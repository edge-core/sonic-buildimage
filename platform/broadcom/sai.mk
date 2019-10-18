BRCM_SAI = libsaibcm_3.5.3.1m-25_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm_3.5.3.1m-25_amd64.deb?sv=2015-04-05&sr=b&sig=kLfhfLeBmENmTXVa%2BZ90k2Fq8ZOQ84kxn5%2FzY3KLV2s%3D&se=2033-06-17T23%3A45%3A50Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.5.3.1m-25_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.5/libsaibcm-dev_3.5.3.1m-25_amd64.deb?sv=2015-04-05&sr=b&sig=a%2BvxIrNcVwnp0CBXS%2BTGiGl%2F%2Fl8mo9ZKPkZyroPY0bI%3D&se=2033-06-17T23%3A45%3A21Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

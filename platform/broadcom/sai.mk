BRCM_SAI = libsaibcm_2.1.5.1-6-20170510001051.32_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-6-20170510001051.32_amd64.deb?sv=2015-04-05&sr=b&sig=PS9GQvhA2n%2BLXtu93KYKybvmmLyeIX%2BcrRZspIBvm5o%3D&se=2031-01-17T07%3A02%3A06Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-6-20170510001051.32_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-6-20170510001051.32_amd64.deb?sv=2015-04-05&sr=b&sig=d2%2BYxTvzjR92hDXx5Wx7gWDQU52wpLzw4ECxNiAwExM%3D&se=2031-01-17T07%3A01%3A37Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

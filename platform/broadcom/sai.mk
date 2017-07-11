BRCM_SAI = libsaibcm_2.1.5.1-15-20170711181855.48_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.1.5.1-15-20170711181855.48_amd64.deb?sv=2015-04-05&sr=b&sig=shAVuRyM%2ByENjVs9QSEDt%2FALvITRS5GoTvC69MJ4G8M%3D&se=2031-03-20T18%3A21%3A43Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.1.5.1-15-20170711181855.48_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.1.5.1-15-20170711181855.48_amd64.deb?sv=2015-04-05&sr=b&sig=oksLplSCyP58%2BYap4JWi%2FgNz2%2BeJtVDbLui1IUDZSbw%3D&se=2031-03-20T18%3A21%3A16Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

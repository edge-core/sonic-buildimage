BRCM_SAI = libsaibcm_2.0.3.7-1_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_2.0.3.7-1_amd64.deb?sv=2015-04-05&sr=b&sig=VCOFP%2FtCWJUZpN04CMHbsSXS7bKMIV%2B14fLbpNBUe4A%3D&se=2030-09-18T19%3A17%3A52Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_2.0.3.7-1_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_2.0.3.7-1_amd64.deb?sv=2015-04-05&sr=b&sig=QeOqPjmYW%2BHqaK3x1JlgCEVeYto0cZeYj6M52vY1Wjw%3D&se=2030-09-18T19%3A18%3A55Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)

$(BRCM_SAI)_DEPENDS += $(BRCM_OPENNSL)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

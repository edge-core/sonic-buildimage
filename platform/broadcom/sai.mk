BRCM_SAI = libsaibcm_3.7.4.2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.4.2_amd64.deb?sv=2015-04-05&sr=b&sig=Iqgd1HDmXOa%2F2OEnez1D4dQ4wVICZlnvVOYao1FYlio%3D&se=2034-01-14T18%3A51%3A07Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.4.2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.4.2_amd64.deb?sv=2015-04-05&sr=b&sig=cbQJOwQcILWYbjuI3LObY6H7bvCNijKfEkdAIrm3Q64%3D&se=2034-01-14T18%3A49%3A15Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

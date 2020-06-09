BRCM_SAI = libsaibcm_3.7.4.2-2_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm_3.7.4.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=sl819d71a%2BcgrDtOt%2BmywfSL9N2EQS58qMJFq0aKqo8%3D&se=2034-02-11T20%3A28%3A46Z&sp=r"
BRCM_SAI_DEV = libsaibcm-dev_3.7.4.2-2_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/bcmsai/3.7/libsaibcm-dev_3.7.4.2-2_amd64.deb?sv=2015-04-05&sr=b&sig=cvOpP0PWFVmBNeYLMkxyI4BFBQf1DopD32t%2B3AkJHRg%3D&se=2034-02-11T20%3A27%3A46Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)

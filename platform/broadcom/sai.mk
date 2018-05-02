BRCM_SAI = libsaibcm_3.1.3.4-11_amd64.deb
$(BRCM_SAI)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm_3.1.3.4-11_amd64.deb?sv=2015-04-05&sr=b&sig=0pctCvAKfSqT8O%2FWSMxw532XAXFsxXdKljQqWfOX8xA%3D&se=2155-03-25T07%3A23%3A41Z&sp=r"

BRCM_SAI_DEV = libsaibcm-dev_3.1.3.4-11_amd64.deb
$(eval $(call add_derived_package,$(BRCM_SAI),$(BRCM_SAI_DEV)))
$(BRCM_SAI_DEV)_URL = "https://sonicstorage.blob.core.windows.net/packages/libsaibcm-dev_3.1.3.4-11_amd64.deb?sv=2015-04-05&sr=b&sig=IO1g%2FdcObkureizN8ZMPqISP6opZXu%2FrHostog6aIrU%3D&se=2155-03-25T08%3A13%3A34Z&sp=r"

SONIC_ONLINE_DEBS += $(BRCM_SAI) $(BRCM_SAI_DEV)
$(BRCM_SAI_DEV)_DEPENDS += $(BRCM_SAI)
